import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import * as docker from "@pulumi/docker";
import * as command from "@pulumi/command";
import { v4 as uuidv4 } from "uuid";

import * as config from "../../config";

export const imageTag = config.isDev ? uuidv4() : "latest";

export const deployImage = (path: string, options: pulumi.ResourceOptions = {}) => {
    const registry = new gcp.container.Registry(`${config.project}-${config.stack}`);

    const registryUrl = registry.id.apply(_ => gcp.container.getRegistryRepository().then(reg => reg.repositoryUrl));
    const imageName = registryUrl.apply(url => `${url}/${config.project}:${imageTag}`);

    const prepareRequirements = new command.local.Command("create-requirements-text", {
        dir: path,
        create: "poetry export --without-hashes --format=requirements.txt > requirements.txt"
    }, options);

    const image = new docker.Image("docker-image", {
        build: {
            context: path,
            dockerfile: `${path}/Dockerfile`,
        },
        imageName,

        registry: {
            server: registryUrl,
        }
    }, {
        ...options,
        dependsOn: [
            prepareRequirements,
        ],
    });

    return image;
};
