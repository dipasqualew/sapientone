import * as pulumi from "@pulumi/pulumi"

export const stack = pulumi.getStack()
export const stackConfig = new pulumi.Config();
export const project = stackConfig.require("GOOGLE_PROJECT");
export const isDev = stack === "dev";
