import { ref, watch } from 'vue';

import { getStorage } from './di';

export interface AppSettings {
    SAPIENTONE_API_KEY: string;
    SAPIENTONE_URL: string;
}

const appSettings = ref<AppSettings>({
    SAPIENTONE_API_KEY: '',
    SAPIENTONE_URL: '',
});

export const useAppSettings = () => {
    return appSettings;
};


const initAppSettings = async () => {
    const storage = getStorage();

    const stored = await storage.get(['SAPIENTONE_API_KEY', 'SAPIENTONE_URL']);

    appSettings.value = {
        SAPIENTONE_API_KEY: stored.SAPIENTONE_API_KEY || "",
        SAPIENTONE_URL: stored.SAPIENTONE_URL || "",
    };

    watch(appSettings.value, async (newSettings) => {
        await storage.set(newSettings);
    });
};

initAppSettings();
