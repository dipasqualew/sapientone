import { createApp, Component } from 'vue'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { App } from 'vue'


const vuetify = createVuetify({
    components,
    directives,
})

interface Dependency {
    symbol: Symbol;
    value: unknown;
}

export const setupApp = (component: Component, root: string, dependencies: Dependency[] = []): App<Element> => {
    const app = createApp(component)
    app.use(vuetify)

    dependencies.forEach((dependency) => {
        app.provide(dependency.symbol, dependency.value);
    });

    app.mount(root)

    return app;
};
