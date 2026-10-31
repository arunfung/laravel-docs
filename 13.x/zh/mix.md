# Laravel Mix

- [简介](#introduction)

<a name="introduction"></a>
## 简介

> [!WARNING]
> Laravel Mix 是一个不再积极维护的旧扩展包。可以使用 [Vite](/docs/{{version}}/vite) 作为现代替代方案。

[Laravel Mix](https://github.com/laravel-mix/laravel-mix) 是由 [Laracasts](https://laracasts.com) 创始人 Jeffrey Way 开发的扩展包，提供流畅的 API，让你使用多种常见的 CSS 和 JavaScript 预处理器为 Laravel 应用定义 [webpack](https://webpack.js.org) 构建步骤。

换句话说，Mix 让编译和压缩应用的 CSS 和 JavaScript 文件变得非常简单。通过简单的方法链，你可以流畅地定义资源处理流程。例如：

```js
mix.js('resources/js/app.js', 'public/js')
    .postCss('resources/css/app.css', 'public/css');
```

如果你曾对如何开始使用 webpack 和编译资源感到困惑或不知所措，你会喜欢 Laravel Mix。不过，开发应用时并非必须使用它；你可以自由选择任何资源处理工具，甚至不使用任何工具。

> [!NOTE]
> 在新安装的 Laravel 应用中，Vite 已经取代了 Laravel Mix。如需查看 Mix 文档，请访问 [Laravel Mix 官方网站](https://laravel-mix.com/)。如果你想切换到 Vite，请参阅我们的 [Vite 迁移指南](https://github.com/laravel/vite-plugin/blob/main/UPGRADE.md#migrating-from-laravel-mix-to-vite)。
