export interface ChromeCompatibleStorageAPI {
    get: (keys: string[]) => Promise<Record<string, string | null>>;
    set: (values: Record<string, string>) => Promise<void>;
};


export interface ChromeCompatibleContextMenuAPI {
    create: (options: chrome.contextMenus.CreateProperties) => void;
}

export const getStorage = (): ChromeCompatibleStorageAPI => {
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

export const getContextMenu = (): ChromeCompatibleContextMenuAPI => {
    if (chrome.contextMenus) {
        return chrome.contextMenus;
    }

    return {
        create: (options: chrome.contextMenus.CreateProperties) => {
            const selector = 'sapientone__fake_context_menu_parent'

            let activeElement: HTMLElement | null = null;
            let parent = document.getElementById(selector);

            if (!parent) {
                parent = document.createElement('div');
                document.body.append(parent);
            }

            parent.style.visibility = 'hidden';

            const option = document.createElement('div');
            option.innerText = options.title || 'UNNAMED OPTION';
            parent.append(option);

            option.addEventListener('click', () => {
                if (activeElement) {
                    activeElement.focus();
                }
                options.onclick!({} as any, {} as any);

                parent && (parent.style.visibility = 'hidden');
            });

            document.addEventListener("keydown", (event) => {
                activeElement = document.activeElement as HTMLElement;

                if (event.key === 'm' && event.ctrlKey) {
                    parent && (parent.style.visibility = 'visible');

                    setTimeout(() => {
                        parent && (parent.style.visibility = 'hidden')
                    }, 3000)
                }
            });
        }
    }
}
