
// extensible dùng register 
export const App = {
    modules: {},
    register(name, module) {
        this.modules[name] = module;
    },
    init() {
        Object.values(this.modules).forEach(m => m.init?.());
    }
};

const moduleList = ["book_module.js", "author_module.js"];

Promise.all(
    moduleList.map(file => import(`/static/modules/${file}`))
).then(() => {
    App.init();
});

