import * as pulumi from "@pulumi/pulumi";
import * as cloudflare from "@pulumi/cloudflare";


export interface DNSRecord {
    name: string;
    type: 'A' | 'CNAME' | 'TXT';
    value: string | pulumi.Output<string>;
    ttl: number;
};


export class CloudflareDNSRecord extends pulumi.ComponentResource {
    record: cloudflare.Record;
    zoneId: string;

    constructor(
        resourceName: string,
        zoneId: string,
        config: DNSRecord,
        opt: pulumi.ComponentResourceOptions = {},
    ) {
        // Register this component with name examples:S3Folder
        super("cloudflare:dns", resourceName, {}, opt);
        this.zoneId = zoneId;

        this.record = new cloudflare.Record(`cloudflare:${resourceName}`, {
            name: config.name,
            zoneId: zoneId,
            type: config.type,
            value: config.value,
            ttl: config.ttl,
        }, {
            deleteBeforeReplace: true,
            replaceOnChanges: ["*"],
            parent: this,
        });

        this.registerOutputs();
    }
}
