import * as pulumi from '@pulumi/pulumi';
import * as gcp from "@pulumi/gcp";

import { project } from '../../config';


export const enableAPIs = (apis: string[]) => {
    return apis.map(async (api) => {
        const reference = `enable-api:${api}.googleapis.com`;

        return new gcp.projects.Service(reference, {
            service: `${api}.googleapis.com`,
            project: project,
        });
    });
};
