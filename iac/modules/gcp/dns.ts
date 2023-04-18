import * as gcp from "@pulumi/gcp";
import * as pulumi from "@pulumi/pulumi";

import { CloudflareDNSRecord } from "../cloudflare/dns"

export interface GCPDomainMappingConstructor {
    domain: string;
    region: string;
    googleProjectId: string;
    cloudFlareZoneId: string;

    /**
     * The name of the Cloud Run service or CloudFunction
     * that this domain mapping applies to.
     */
    routeName: string | pulumi.Output<string>;
}

// Define a component for serving a static website on S3
export class GCPDomainMapping extends pulumi.ComponentResource {
    constructor(args: GCPDomainMappingConstructor, options: pulumi.ComponentResourceOptions = {}) {
        // Register this component with name examples:S3Folder
        super("domain-mapping", args.domain, {}, options);

        // Configure the Cloud Run domain mapping
        const domainMapping = new gcp.cloudrun.DomainMapping(`mapping`, {
            metadata: {
                namespace: args.googleProjectId,
            },
            location: args.region,
            name: args.domain,
            spec: {
                routeName: args.routeName,
            },
        }, {
            deleteBeforeReplace: true,
            replaceOnChanges: ["*"],
            parent: this,
        });

        const status = domainMapping.statuses[0];

        const records = status.resourceRecords as unknown as Array<{ rrdata: pulumi.Output<string> }>;
        const record = records[0];

        const dnsConfig = record.rrdata.apply((value) => {
            return {
                name: args.domain,
                zoneId: args.cloudFlareZoneId,
                type: "CNAME",
                value: value,
                ttl: 1,
            }
        }) as unknown as any;

        const _record = new CloudflareDNSRecord(args.domain, args.cloudFlareZoneId, dnsConfig, { parent: this });

        this.registerOutputs();
    }
}
