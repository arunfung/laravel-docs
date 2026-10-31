
# Laravel Mix

-   [介绍](#introduction)

## 介绍

[Laravel Mix](https://github.com/laravel-mix/laravel-mix?utm_source=chatgpt.com) 是由 [Laracasts](https://laracasts.com?utm_source=chatgpt.com) 创始人 Jeffrey Way 开发的一个包，它提供了一个简洁的 API，用于在你的 Laravel 应用中定义 [webpack](https://webpack.js.org?utm_source=chatgpt.com) 构建步骤，同时支持多种常用的 CSS 和 JavaScript 预处理器。

换句话说，Mix 让编译和压缩你的应用的 CSS 和 JavaScript 文件变得非常简单。通过简单的方法链，你可以流畅地定义你的资源处理流程。例如：

```js
mix.js('resources/js/app.js', 'public/js')
    .postCss('resources/css/app.css', 'public/css');
```

如果你曾经对如何开始使用 webpack 和资源编译感到困惑或不知所措，那么你一定会喜欢 Laravel Mix。不过，你在开发应用时并不是必须使用它；你可以自由选择任何资源处理工具，甚至可以不使用任何工具。

> [!注意]
> 在新的 Laravel 安装中，Vite 已经取代了 Laravel Mix。如需查看 Mix 的文档，请访问 [Laravel Mix 官方网站](https://laravel-mix.com/?utm_source=chatgpt.com)。如果你想切换到 Vite，请参阅我们的 [Vite 迁移指南](https://github.com/laravel/vite-plugin/blob/main/UPGRADE.md?utm_source=chatgpt.com#migrating-from-laravel-mix-to-vite)。
