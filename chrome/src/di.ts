export interface ChromeCompatibleStorage {
    get: (keys: string[]) => Promise<Record<string, string | null>>;
    set: (values: Record<string, string>) => Promise<void>;
};

export const getStorage = (): ChromeCompatibleStorage => {
    if (chrome.storage) {
        return chrome.storage.local;
    }

    return {
        get: (keys: string[]) => {
            const result: Record<string, string | null> = {};
            keys.forEach((key) => {
                result[key] = localStorage.getItem(key);
            });

            return Promise.resolve(result);
        },
        set: (values: Record<string, unknown>) => {
            Object.keys(values).forEach((key) => {
                localStorage.setItem(key, values[key] as string);
            });

            return Promise.resolve();
        }
    }
}
