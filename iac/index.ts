import * as dotenv from 'dotenv'
import * as pulumi from '@pulumi/pulumi'

import { enableAPIs } from './modules/gcp/utils';
import { createSecrets } from './modules/gcp/secrets';
import { deployImage } from './modules/gcp/containers';
import { GCPCloudRunService } from './modules/gcp/cloudrun';
import { stackConfig } from './config';

dotenv.config({ path: '../.env' })

const REQUIRED_APIS = [
    // Also remember to authenticate docker:
    // cat ${GOOGLE_APPLICATION_CREDENTIALS} | docker login -u _json_key --password-stdin https://gcr.io

    // Also remember to verify the domain against the service user
    // https://www.google.com/webmasters/verification/details?hl=en&domain=your-parent-domain.com
    // email can be found in the json key file
    "cloudresourcemanager",
    "iam",
    'secretmanager',
    'containerregistry',
    "run",
];


const main = () => {
    const enabledAPIs = enableAPIs(REQUIRED_APIS);

    const secrets = createSecrets(['OPENAI_API_KEY', 'SAPIENTONE_API_KEY', 'PGVECTOR_CONNECTION_STRING'] as const, { dependsOn: enabledAPIs });

    const image = deployImage("../lambdas");

    const cloudRunAnswerQuestion = new GCPCloudRunService({
        zoneId: stackConfig.require("CLOUDFLARE_ZONE_ID"),
        allowUnauthorized: true,
        appConfig: {
            name: 'memory-service',
            image: image,
            port: 8080,
            secrets: [
                {
                    key: 'OPENAI_API_KEY',
                    secret: secrets.OPENAI_API_KEY,
                },
                {
                    key: 'SAPIENTONE_API_KEY',
                    secret: secrets.SAPIENTONE_API_KEY,
                },
                {
                    key: 'PGVECTOR_CONNECTION_STRING',
                    secret: secrets.PGVECTOR_CONNECTION_STRING,
                }
            ],
            envs: [],
        },
    }, {
        dependsOn: [image, ...Object.values(secrets)],
    });

    return {
        images: {
            memoryService: {
                name: image.imageName,
                server: image.registryServer,
            },
        },
        secrets: {
            OPENAI_API_KEY: secrets.OPENAI_API_KEY.outputs,
            SAPIENTONE_API_KEY: secrets.SAPIENTONE_API_KEY.outputs,
            PGVECTOR_CONNECTION_STRING: secrets.PGVECTOR_CONNECTION_STRING.outputs,
        },
        services: {
            memoryService: {
                name: cloudRunAnswerQuestion.name,
                region: cloudRunAnswerQuestion.region,
                serviceAccount: cloudRunAnswerQuestion.serviceAccount,
                urls: {
                    domain: `https://${cloudRunAnswerQuestion.url}`,
                    gcloud: cloudRunAnswerQuestion.gcloudUrl,
                }
            },
        },
    };
}

const outputs = main();

export const images = outputs.images;
export const secrets = outputs.secrets;
export const services = outputs.services;
