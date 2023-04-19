import { ref, watch } from 'vue';

import { getStorage } from './di';

export interface AppSettings {
    SAPIENTONE_API_KEY: string;
    SAPIENTONE_URL: string;
    NOTION_INTEGRATION_KEY: string;
}

const appSettings = ref<AppSettings>({
    SAPIENTONE_API_KEY: '',
    SAPIENTONE_URL: '',
    NOTION_INTEGRATION_KEY: '',
});

export const useAppSettings = () => {
    return appSettings;
};


const initAppSettings = async () => {
    const storage = getStorage();

    const stored = await storage.get(['SAPIENTONE_API_KEY', 'SAPIENTONE_URL', 'NOTION_INTEGRATION_KEY']);

    appSettings.value = {
        SAPIENTONE_API_KEY: stored.SAPIENTONE_API_KEY || "",
        SAPIENTONE_URL: stored.SAPIENTONE_URL || "",
        NOTION_INTEGRATION_KEY: stored.NOTION_INTEGRATION_KEY || "",
    };

    watch(appSettings.value, async (newSettings) => {
        await storage.set(newSettings);
    });
};

initAppSettings();
