import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import { local } from '@pulumi/command'
import { asset } from "@pulumi/pulumi";

import { getSecretAccessorRoles, GCPFunctionSecretDefinition } from "./secrets";
import { stack } from "../../config";



export interface GCPFunctionArgs {
    functionName: string;
    googleProjectId: string;
    cloudflareZoneId: string;
    region: string;
    path: string;
    secrets: GCPFunctionSecretDefinition[];
    env: Record<string, string>;
}

// Define a component for serving a static website on S3
export class GCPFunction extends pulumi.ComponentResource {
    bucket: pulumi.Output<string>;
    endpoint: pulumi.Output<string>;

    constructor(args: GCPFunctionArgs, opt: pulumi.ComponentResourceOptions = {}) {
        // Register this component with name examples:S3Folder
        super("gcp:cloud-function-http", args.functionName, {}, opt);

        // Create a service account for the Cloud Function
        const serviceAccount = new gcp.serviceaccount.Account(`${args.functionName}--function-sa`, {
            accountId: `${args.functionName}-sa`,
            displayName: `${args.functionName} Service Account`,
        }, {
            parent: this,
        });

        const secretAccessorRoles = getSecretAccessorRoles(this, args.functionName, serviceAccount, args.secrets);

        const secretEnvironmentVariables = args.secrets.map((el) => {
            const envSecret = {
                key: el.key,
                secret: el.secret.secretId,
                version: el.secret.currentVersion,
            }

            return envSecret;
        });

        const bucket = new gcp.storage.Bucket(`${args.functionName}--function-bucket`, {
            forceDestroy: true,
            location: "EU",
        }, {
            parent: this,
        });

        const prepareRequirements = new local.Command(`${args.functionName}--prepare-requirements`, {
            create: `cd ${args.path} && poetry export -f requirements.txt --output requirements.txt`,
        }, {
            parent: this,
        });

        // Google Cloud Function in Python

        const bucketObjectPython = new gcp.storage.BucketObject(`${args.functionName}--function-zip`, {
            bucket: bucket.name,
            source: new asset.AssetArchive({
                ".": new asset.FileArchive(args.path),
            }),
        }, {
            dependsOn: [bucket, prepareRequirements],
            replaceOnChanges: ["source"],
            deleteBeforeReplace: true,
            parent: this,
        });



        const functionPython = new gcp.cloudfunctions.Function(`${args.functionName}--function`, {
            name: `${stack}--${args.functionName}`,
            sourceArchiveBucket: bucket.name,
            runtime: "python39",
            project: args.googleProjectId,
            sourceArchiveObject: bucketObjectPython.name,
            entryPoint: this.getFunctionHandlerName(args.functionName),
            triggerHttp: true,
            availableMemoryMb: 512,
            serviceAccountEmail: serviceAccount.email,
            region: 'europe-west1',
            environmentVariables: args.env,
            secretEnvironmentVariables: secretEnvironmentVariables,
        }, {
            dependsOn: [
                bucketObjectPython,
                serviceAccount,
                ...secretAccessorRoles,
            ],
            parent: this,
            customTimeouts: {
                create: "15m",
                update: "15m",
            },
        });

        const pyInvoker = new gcp.cloudfunctions.FunctionIamMember(`${args.functionName}--function-invoker`, {
            project: functionPython.project,
            region: functionPython.region,
            cloudFunction: functionPython.name,
            role: "roles/cloudfunctions.invoker",
            member: "allUsers",
        }, {
            dependsOn: [functionPython],
            parent: this,
        });

        this.bucket = bucket.name;
        this.endpoint = functionPython.httpsTriggerUrl;

        // Register that we are done constructing the component
        this.registerOutputs();
    }

    getFunctionHandlerName(functionName: string): string {
        return functionName.replace(/-/g, '_') + "_handler";
    }
}
