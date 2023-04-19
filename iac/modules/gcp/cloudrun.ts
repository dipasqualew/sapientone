import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import * as docker from "@pulumi/docker"

import { GCPDomainMapping } from "./dns";
import { getSecretAccessorRoles, GCPFunctionSecretDefinition } from "./secrets";
import { project, stack, stackConfig } from "../../config";


export interface AppEnvVariable {
    name: string;
    value: string | pulumi.Output<string>;
}

export interface AppEnvSecret {
    name: string;
    valueSource: {
        secretKeyRef: {
            secret: pulumi.Output<string>,
            version: pulumi.Output<string>,
        },
    };
}

export interface AppConfiguration {
    name: string;
    image: string | docker.Image;
    port: number;
    envs: AppEnvVariable[];
    secrets: GCPFunctionSecretDefinition[]
}

export interface GCPCloudRunServiceConstructor {
    appConfig: AppConfiguration;
    zoneId: string;
    allowUnauthorized?: boolean;
}


export class GCPCloudRunService extends pulumi.ComponentResource {
    name: string;
    region: string;
    url: string;
    serviceAccount: pulumi.Output<string>;
    gcloudUrl: pulumi.Output<string>;

    constructor(config: GCPCloudRunServiceConstructor, opt: pulumi.ComponentResourceOptions = {}) {
        super("gcp:cloudrun", config.appConfig.name, {}, opt);

        this.name = config.appConfig.name;
        this.region = stackConfig.require("region");
        this.url = `${config.appConfig.name}.${stack}.${stackConfig.require("base_domain")}`;

        const access = this.setupAccess(project, config.appConfig.secrets);

        this.serviceAccount = access.account.email;

        const imageName = typeof config.appConfig.image === 'string'
            ? config.appConfig.image
            : config.appConfig.image.imageName;

        const service = this.setupService(
            imageName,
            config.appConfig.envs,
            access.secrets,
            config.appConfig.port,
            access.account,
            config.zoneId,
        );

        if (config.allowUnauthorized) {
            this.allowUnauthorized(service);
        }

        this.gcloudUrl = service.uri;

        this.registerOutputs();
    }

    get prefix(): string {
        return `${this.name}-${stack}`;
    }

    setupAccess(project: string, secrets: GCPFunctionSecretDefinition[] = []) {
        const serviceAccount = new gcp.serviceaccount.Account(`${this.prefix}-sa`, {
            accountId: `${this.prefix}-sa`,
            displayName: "Cloud Run Service Account",
        }, {
            parent: this,
        });

        const secretAccessorRoles = getSecretAccessorRoles(this, this.prefix, serviceAccount, secrets);

        // Grant the service account the necessary IAM roles
        const serviceAccountIam = new gcp.projects.IAMBinding(`${this.prefix}-iam`, {
            project: project,
            role: "roles/run.admin",
            members: [serviceAccount.email.apply((email) => `serviceAccount:${email}`)],
        }, {
            dependsOn: [serviceAccount, ...secretAccessorRoles],
            parent: this,
        });

        return {
            account: serviceAccount,
            iamBinding: serviceAccountIam,
            secrets: secrets.map((el) => {
                return {
                    name: el.key,
                    valueSource: {
                        secretKeyRef: {
                            secret: el.secret.secretId,
                            version: el.secret.currentVersion,
                        }
                    }
                }
            }),
        }
    }

    setupService(
        imageName: string | pulumi.Output<string>,
        envs: AppEnvVariable[],
        secrets: AppEnvSecret[],
        port: number,
        serviceAccount: gcp.serviceaccount.Account,
        cloudFlareZoneId: string,
    ) {
        const combinedEnvs = [
            ...envs,
            ...secrets,
        ];

        const service = new gcp.cloudrunv2.Service(`${this.prefix}-service`, {
            name: `${project}--${stack}--${this.name}`,
            location: this.region,
            template: {
                containers: [
                    {
                        image: imageName,
                        envs: combinedEnvs,
                        ports: [
                            { containerPort: port },
                        ],

                    },
                ],
                serviceAccount: serviceAccount.email,
                annotations: {
                    "autoscaling.knative.dev/minScale": "0",
                    "autoscaling.knative.dev/maxScale": "1",
                },
            },
        }, { dependsOn: [serviceAccount], parent: this, });

        new GCPDomainMapping({
            googleProjectId: project,
            domain: this.url,
            region: this.region,
            cloudFlareZoneId,
            routeName: service.name,
        }, {
            parent: this,
            dependsOn: [service],
        });

        return service;
    }

    allowUnauthorized(service: gcp.cloudrunv2.Service) {
        // Allow unauthenticated users to access the Cloud Run service
        new gcp.cloudrun.IamMember(`${this.prefix}-unauth`, {
            location: this.region,
            service: service.name,
            member: "allUsers",
            role: "roles/run.invoker",
        }, {
            dependsOn: [service],
            parent: this
        });

    }

}
