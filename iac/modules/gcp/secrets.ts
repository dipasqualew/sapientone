import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";

import { stackConfig, stack } from "../../config";


export interface SecretOutput {
    key: string;
    secret: pulumi.Output<string>;
    version: pulumi.Output<string>;
};

export interface GCPFunctionSecretDefinition {
    key: string;
    secret: GCPSecret,
}

export class GCPSecret extends pulumi.ComponentResource {
    id: pulumi.Output<string>;
    secretId: pulumi.Output<string>
    name: pulumi.Output<string>;
    currentVersion: pulumi.Output<string>;
    value: pulumi.Output<string>;
    outputs: {
        name: pulumi.Output<string>;
        value: pulumi.Output<string>;
    }

    constructor(secretName: string, secretValue?: string, opt: pulumi.ComponentResourceOptions = {}) {
        // Register this component with name examples:S3Folder
        super("gcp:secret", secretName, {}, opt);

        // create secrets
        const secretRef = new gcp.secretmanager.Secret(`secret:${stack}:${secretName}`, {
            replication: {
                automatic: true,
            },
            secretId: `${stack}--${secretName}`,
        }, {
            parent: this,
            deleteBeforeReplace: true,
        });

        const version = new gcp.secretmanager.SecretVersion(`secret-version:${stack}:${secretName}`, {
            secret: secretRef.id,
            secretData: secretValue || stackConfig.requireSecret(secretName),
        }, {
            parent: this,
            deleteBeforeReplace: true,
        });

        this.id = secretRef.id;
        this.secretId = secretRef.secretId;
        this.name = secretRef.name;
        this.currentVersion = version.version;
        this.value = version.secretData;

        this.outputs = {
            name: this.name,
            value: this.value,
        };

        this.registerOutputs();
    }
};

export const createSecrets = <T extends readonly string[]>(secretNames: T, options: pulumi.ComponentResourceOptions = {}): Record<T[number], GCPSecret> => {
    return Object.fromEntries(secretNames.map((secretName) => {
        const entry = [
            secretName as T[number],
            new GCPSecret(secretName, undefined, options),
        ];

        return entry;
    }));
}

export const getSecretAccessorRoles = (
    parent: pulumi.Resource,
    identifier: string,
    serviceAccount: gcp.serviceaccount.Account,
    secrets: GCPFunctionSecretDefinition[]
): gcp.secretmanager.SecretIamMember[] => {
    const member = serviceAccount.email.apply(email => `serviceAccount:${email}`);

    const roles = secrets.map((el) => {
        const resourceName = `${identifier}--${el.key}--function-secret-accessor`;

        return new gcp.secretmanager.SecretIamMember(resourceName, {
            secretId: el.secret.id,
            role: "roles/secretmanager.secretAccessor",
            member: member,
        }, {
            parent,
        });

    });

    return roles;
}
