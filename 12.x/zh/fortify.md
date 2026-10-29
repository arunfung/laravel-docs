
# Laravel Fortify

-   [简介](#introduction)
    -   [什么是 Fortify?](#what-is-fortify)
    -   [我什么时候应该使用 Fortify?](#when-should-i-use-fortify)
-   [安装](#installation)
    -   [Fortify 功能](#fortify-features)
    -   [禁用视图](#disabling-views)
-   [认证](#authentication)
    -   [自定义用户认证](#customizing-user-authentication)
    -   [自定义认证管道](#customizing-the-authentication-pipeline)
    -   [自定义重定向](#customizing-authentication-redirects)
-   [双重身份验证](#two-factor-authentication)
    -   [启用双重身份验证](#enabling-two-factor-authentication)
    -   [使用双重身份验证登录](#authenticating-with-two-factor-authentication)
    -   [禁用双重身份验证](#disabling-two-factor-authentication)
-   [注册](#registration)
    -   [自定义注册](#customizing-registration)
-   [密码重置](#password-reset)
    -   [请求密码重置链接](#requesting-a-password-reset-link)
    -   [重置密码](#resetting-the-password)
    -   [自定义密码重置](#customizing-password-resets)
-   [邮箱验证](#email-verification)
    -   [保护路由](#protecting-routes)
-   [密码确认](#password-confirmation)

## 简介

[Laravel Fortify](https://github.com/laravel/fortify?utm_source=chatgpt.com) 是一个与前端无关的 Laravel **认证后端实现**。
Fortify 会注册实现 Laravel 所有认证功能所需的路由和控制器，包括登录、注册、密码重置、邮箱验证等。

安装 Fortify 后，你可以运行 `route:list` Artisan 命令，查看 Fortify 已经注册的路由。

由于 Fortify 本身不提供用户界面，因此它需要与你自己的用户界面配合使用，而你的前端界面需要向 Fortify 注册的这些路由发起请求。
在后续文档中，我们将具体说明如何向这些路由发起请求。

> [!注意]
> 请记住，Fortify 是一个用于帮助你快速实现 Laravel 认证功能的包。
> **你并不一定要使用它。**
> 你始终可以选择手动与 Laravel 的认证服务交互，参考 [authentication](/docs/laravel/12.x/authentication)、[password reset](/docs/laravel/12.x/passwords)、[email verification](/docs/laravel/12.x/verification) 文档来实现。



### 什么是 Fortify?

正如前面提到的，Laravel Fortify 是一个与前端无关的 Laravel **认证后端实现**。
Fortify 会注册实现 Laravel 所有认证功能所需的路由和控制器，包括：登录、注册、密码重置、邮箱验证等等。

**你并不需要使用 Fortify 才能使用 Laravel 的认证功能。**
你始终可以选择手动与 Laravel 的认证服务交互，参考 [authentication](/docs/laravel/12.x/authentication)、[password reset](/docs/laravel/12.x/passwords)、[email verification](/docs/laravel/12.x/verification) 文档来实现。

如果你是 Laravel 新手，你可能希望先探索 [应用程序入门套件（starter kits）](/docs/laravel/12.x/starter-kits)，再尝试使用 Laravel Fortify。
我们的入门套件提供了完整的认证脚手架，其中包含一个使用 [Tailwind CSS](https://tailwindcss.com?utm_source=chatgpt.com) 构建的用户界面。
这样，你可以先学习并熟悉 Laravel 的认证功能，然后再让 Laravel Fortify 来实现这些功能。

本质上，Laravel Fortify 把应用程序入门套件中的 **路由和控制器** 拆分出来，打包为一个不包含用户界面的独立包。
这让你可以快速搭建应用的认证后端实现，而不受任何前端框架或界面风格的限制。

### 我什么时候应该使用 Fortify?

你可能会想，什么时候适合使用 Laravel Fortify？
首先，如果你正在使用 Laravel 的某个 [应用程序入门套件](/docs/laravel/12.x/starter-kits)，那么 **你不需要安装 Laravel Fortify**，因为所有的入门套件已经提供了完整的认证实现。



如果你没有使用应用程序入门套件，并且你的应用需要认证功能，你有两个选择：

1.  **手动实现**应用的认证功能；
2.  **使用 Laravel Fortify** 来提供这些功能的后端实现。

如果你选择安装 Fortify，你的用户界面需要向 Fortify 的认证路由（本文件会详细说明）发起请求，以完成用户的认证和注册。

如果你选择不使用 Fortify，而是手动与 Laravel 的认证服务交互，你也可以这么做，只需参考 [authentication](/docs/laravel/12.x/authentication)、[password reset](/docs/laravel/12.x/passwords)、[email verification](/docs/laravel/12.x/verification) 文档。

#### Laravel Fortify 与 Laravel Sanctum

有些开发者会对 [Laravel Sanctum](/docs/laravel/12.x/sanctum) 和 Laravel Fortify 之间的区别感到困惑。
因为这两个包解决的是 **不同但相关的问题**，所以 **Laravel Fortify 和 Laravel Sanctum 并不是互斥的或竞争关系的包**。

Laravel Sanctum 只负责管理 API token，并通过会话 cookie 或 token 来验证现有用户。Sanctum **不会提供任何处理用户注册、密码重置等功能的路由**。

如果你正尝试手动构建一个 **为 API 提供服务** 或 **作为单页应用的后端** 的认证层，那么你很可能会同时使用：

-   **Laravel Fortify**（用于用户注册、密码重置等）；

-   **Laravel Sanctum**（用于 API token 管理和会话认证）。

## 安装

首先，使用 Composer 包管理器安装 Fortify：

```shell
composer require laravel/fortify
```



接下来，使用 `fortify:install` Artisan 命令发布 Fortify 的资源：

```shell
php artisan fortify:install
```

该命令会将 Fortify 的操作（actions）发布到你的 `app/Actions` 目录，如果目录不存在，会自动创建。
此外，还会发布 **FortifyServiceProvider**、配置文件，以及所有必要的数据库迁移文件。

接下来，你应该迁移数据库：

```shell
php artisan migrate
```

### Fortify 功能（Fortify Features）

`fortify` 配置文件中包含一个 `features` 配置数组。
该数组定义了 Fortify 默认将暴露的后端路由/功能。

我们建议你只启用以下功能，这些是大多数 Laravel 应用提供的基本认证功能：

```php
'features' => [
    Features::registration(),
    Features::resetPasswords(),
    Features::emailVerification(),
],
```

### 禁用视图（Disabling Views）

默认情况下，Fortify 定义了一些旨在返回视图的路由，例如登录页面或注册页面。
然而，如果你正在构建一个 JavaScript 驱动的单页应用（SPA），你可能不需要这些路由。
因此，你可以在应用的 `config/fortify.php` 配置文件中将 `views` 配置值设置为 `false`，以完全禁用这些路由：

```php
'views' => false,
```

#### 禁用视图与密码重置（Disabling Views and Password Reset）

如果你选择禁用 Fortify 的视图，但仍需要实现应用的密码重置功能，你仍然应该定义一个名为 `password.reset` 的路由，用于显示应用的“重置密码”视图。

这是必要的，因为 Laravel 的 `Illuminate\Auth\Notifications\ResetPassword` 通知会通过 `password.reset` 命名路由生成密码重置 URL。



## 认证

首先，我们需要告诉 Fortify 如何返回我们的 **登录视图（login view）**。
请记住，Fortify 是一个 **无前端（headless）的认证库**。
如果你希望使用已经完成的 Laravel 认证功能的前端实现，你应该使用 [应用程序入门套件（application starter kit）](/docs/laravel/12.x/starter-kits)。

所有认证视图的渲染逻辑都可以通过 `Laravel\Fortify\Fortify` 类提供的相应方法进行自定义。
通常，你应该在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用这些方法。
Fortify 会帮你定义返回该视图的 `/login` 路由：

```php
use Laravel\Fortify\Fortify;

/**
 * 引导应用服务
 */
public function boot(): void
{
    Fortify::loginView(function () {
        return view('auth.login');
    });

    // ...
}
```

你的登录模板应包含一个表单，该表单向 `/login` 发起 **POST 请求**。
`/login` 接口期望收到一个字符串类型的 `email` / `username` 和一个 `password`。
邮箱/用户名字段的名称应与 `config/fortify.php` 配置文件中的 `username` 值匹配。
此外，还可以提供一个布尔型字段 `remember`，用于指示用户是否希望使用 Laravel 提供的 **记住我（remember me）** 功能。

如果登录尝试成功，Fortify 会重定向到应用的 `fortify` 配置文件中通过 `home` 配置选项设置的 URI。
如果登录请求是 XHR 请求，则会返回 **200 HTTP 响应**。

如果登录请求失败，用户将被重定向回登录页面，验证错误信息可通过共享的 `$errors` [Blade 模板变量](/docs/laravel/12.x/validation#quick-displaying-the-validation-errors) 获取。
如果是 XHR 请求，验证错误会随 **422 HTTP 响应** 一起返回。



### 自定义用户认证（Customizing User Authentication）

Fortify 会根据提供的凭证和应用配置的认证 guard **自动检索并认证用户**。
然而，有时你可能希望 **完全自定义登录凭证的认证方式以及用户的检索方式**。
幸运的是，Fortify 允许你使用 `Fortify::authenticateUsing` 方法轻松实现这一点。

该方法接受一个闭包（closure），闭包接收传入的 HTTP 请求。
闭包负责验证请求附带的登录凭证，并返回对应的用户实例。
如果凭证无效或未找到用户，闭包应返回 `null` 或 `false`。
通常，这个方法应该在 `FortifyServiceProvider` 的 `boot` 方法中调用：

```php
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Laravel\Fortify\Fortify;

/**
 * 引导应用服务
 */
public function boot(): void
{
    Fortify::authenticateUsing(function (Request $request) {
        $user = User::where('email', $request->email)->first();

        if ($user &&
            Hash::check($request->password, $user->password)) {
            return $user;
        }
    });

    // ...
}
```

#### 认证 Guard（Authentication Guard）

你可以在应用的 `fortify` 配置文件中自定义 Fortify 使用的认证 guard。
但是，你应该确保配置的 guard 是 `Illuminate\Contracts\Auth\StatefulGuard` 的实现。

如果你打算使用 Laravel Fortify 对 SPA（单页应用）进行认证，应该使用 Laravel 默认的 `web` guard，并结合 [Laravel Sanctum](https://laravel.com/docs/sanctum?utm_source=chatgpt.com) 使用。

### 自定义认证管道（Customizing the Authentication Pipeline）

Laravel Fortify 会通过一组可调用类（invokable classes）来认证登录请求。
如果你愿意，你可以定义一个 **自定义的管道（pipeline）**，让登录请求按顺序经过这些类。

每个类都应该有一个 `__invoke` 方法，该方法接收传入的 `Illuminate\Http\Request` 实例，并像 [中间件（middleware）](/docs/laravel/12.x/middleware) 一样，接收一个 `$next` 变量，用于将请求传递给管道中的下一个类。



你可以使用 `Fortify::authenticateThrough` 方法来定义你的自定义管道（pipeline）。
该方法接受一个闭包（closure），闭包应返回一个类数组，这些类将按顺序处理登录请求。
通常，这个方法应该在 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用。

下面的示例包含了默认的管道定义，你可以以此为起点进行自定义修改：

```php
use Laravel\Fortify\Actions\AttemptToAuthenticate;
use Laravel\Fortify\Actions\CanonicalizeUsername;
use Laravel\Fortify\Actions\EnsureLoginIsNotThrottled;
use Laravel\Fortify\Actions\PrepareAuthenticatedSession;
use Laravel\Fortify\Actions\RedirectIfTwoFactorAuthenticatable;
use Laravel\Fortify\Features;
use Laravel\Fortify\Fortify;
use Illuminate\Http\Request;

Fortify::authenticateThrough(function (Request $request) {
    return array_filter([
            config('fortify.limiters.login') ? null : EnsureLoginIsNotThrottled::class,
            config('fortify.lowercase_usernames') ? CanonicalizeUsername::class : null,
            Features::enabled(Features::twoFactorAuthentication()) ? RedirectIfTwoFactorAuthenticatable::class : null,
            AttemptToAuthenticate::class,
            PrepareAuthenticatedSession::class,
    ]);
});
```

#### 认证限流（Authentication Throttling）

默认情况下，Fortify 会使用 `EnsureLoginIsNotThrottled` 中间件对认证尝试进行限流。
该中间件会针对 **用户名和 IP 地址组合** 的唯一尝试进行限流。

有些应用可能需要不同的认证限流方式，例如只按 IP 地址进行限流。
因此，Fortify 允许你通过 `fortify.limiters.login` 配置选项指定自己的 [速率限制器（rate limiter）](/docs/laravel/12.x/routing#rate-limiting)。
当然，该配置选项位于应用的 `config/fortify.php` 配置文件中。

> [!注意]
> 将限流、[双重身份验证](/docs/laravel/12.x/fortify#two-factor-authentication) 以及外部 Web 应用防火墙（WAF）结合使用，可以为你的合法应用用户提供最强的防护。



### 自定义重定向（Customizing Redirects）

如果登录尝试成功，Fortify 会将用户重定向到应用 `fortify` 配置文件中通过 `home` 配置选项设置的 URI。
如果登录请求是 XHR 请求，则会返回 **200 HTTP 响应**。
当用户登出应用时，用户将被重定向到 `/` URI。

如果你需要对这一行为进行高级自定义，可以将 `LoginResponse` 和 `LogoutResponse` 接口的实现绑定到 Laravel 的 [服务容器（service container）](/docs/laravel/12.x/container) 中。
通常，这应在应用 `App\Providers\FortifyServiceProvider` 类的 `register` 方法中完成：

```php
use Laravel\Fortify\Contracts\LogoutResponse;

/**
 * 注册应用服务
 */
public function register(): void
{
    $this->app->instance(LogoutResponse::class, new class implements LogoutResponse {
        public function toResponse($request)
        {
            return redirect('/');
        }
    });
}
```

## 双重认证

当启用 Fortify 的双重认证功能时，用户在认证过程中需要输入 **六位数字的动态令牌（token）**。
该令牌使用 **基于时间的一次性密码（TOTP）** 生成，可通过任意兼容 TOTP 的移动认证应用获取，例如 Google Authenticator。

在开始之前，你应确保应用的 `App\Models\User` 模型使用了 `Laravel\Fortify\TwoFactorAuthenticatable` trait：

Before getting started, you should first ensure that your application's `App\Models\User` model uses the `Laravel\Fortify\TwoFactorAuthenticatable` trait:

```php
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Fortify\TwoFactorAuthenticatable;

class User extends Authenticatable
{
    use Notifiable, TwoFactorAuthenticatable;
}
```

接下来，你应在应用中构建一个界面，让用户管理双重认证设置。
该界面应允许用户 **启用和禁用双重认证**，并 **重新生成双重认证恢复码**。

> 默认情况下，`fortify` 配置文件的 `features` 数组指示 Fortify 的双重认证设置在修改前需要 **密码确认**。
> 因此，在继续之前，你的应用应先实现 Fortify 的 [密码确认](#password-confirmation) 功能。




### 启用双因素认证

要开始启用双因素认证，你的应用程序应该向 Fortify 定义的 `/user/two-factor-authentication` 端点发送一个 **POST** 请求。如果请求成功，用户将被重定向回之前的 URL，并且 `status` 会话变量将被设置为 `two-factor-authentication-enabled`。你可以在模板中检测这个 `status` 会话变量，以显示相应的成功消息。如果请求是 XHR 请求，则会返回 `200` HTTP 响应。

在选择启用双因素认证后，用户仍然必须通过提供有效的双因素认证代码来“确认”他们的双因素认证配置。因此，你的“成功”消息应该提示用户仍需确认双因素认证：

```html
@if (session('status') == 'two-factor-authentication-enabled')
    <div class="mb-4 font-medium text-sm">
        Please finish configuring two factor authentication below.
    </div>
@endif
```

接下来，你应该显示用户用于扫描到身份验证器应用的双因素认证二维码。如果你使用 Blade 来渲染应用的前端，可以通过用户实例的 `twoFactorQrCodeSvg` 方法获取二维码 SVG：

```php
$request->user()->twoFactorQrCodeSvg();
```

如果你使用的是 JavaScript 驱动的前端，可以通过 XHR GET 请求 `/user/two-factor-qr-code` 端点来获取用户的双因素认证二维码。该端点将返回一个包含 `svg` 键的 JSON 对象。

#### 确认双因素认证

除了显示用户的双因素认证二维码外，你还应该提供一个文本输入框，让用户提供有效的认证代码以“确认”他们的双因素认证配置。该代码应通过 **POST** 请求提交到 Fortify 定义的 `/user/confirmed-two-factor-authentication` 端点。

如果请求成功，用户将被重定向回之前的 URL，并且 `status` 会话变量将被设置为 `two-factor-authentication-confirmed`：

```html
@if (session('status') == 'two-factor-authentication-confirmed')
    <div class="mb-4 font-medium text-sm">
        Two factor authentication confirmed and enabled successfully.
    </div>
@endif
```



如果对双因素认证确认端点的请求是通过 XHR 发起的，将返回 `200` HTTP 响应。

#### 显示恢复码

你还应该显示用户的双因素恢复码。这些恢复码允许用户在丢失手机设备访问权限时进行认证。如果你使用 Blade 渲染应用的前端，可以通过已认证的用户实例访问恢复码

```php
(array) $request->user()->recoveryCodes()
```

如果你使用的是 JavaScript 驱动的前端，可以通过 XHR GET 请求 `/user/two-factor-recovery-codes` 端点获取用户的恢复码。该端点将返回一个包含用户恢复码的 JSON 数组。

要重新生成用户的恢复码，你的应用程序应向 `/user/two-factor-recovery-codes` 端点发送 **POST** 请求。

### 使用双因素认证进行认证

在认证过程中，Fortify 会自动将用户重定向到应用的双因素认证挑战页面。然而，如果你的应用是通过 XHR 登录请求的，在成功认证后返回的 JSON 响应将包含一个带有 `two_factor` 布尔属性的 JSON 对象。你应该检查此值，以确定是否需要重定向到应用的双因素认证挑战页面。

要开始实现双因素认证功能，我们需要告诉 Fortify 如何返回我们的双因素认证挑战视图。Fortify 的所有认证视图渲染逻辑都可以通过 `Laravel\Fortify\Fortify` 类提供的相应方法进行自定义。通常，你应该在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用此方法：


```php
use Laravel\Fortify\Fortify;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    Fortify::twoFactorChallengeView(function () {
        return view('auth.two-factor-challenge');
    });

    // ...
}
```



Fortify 会负责定义返回该视图的 `/two-factor-challenge` 路由。你的 `two-factor-challenge` 模板应包含一个表单，该表单向 `/two-factor-challenge` 端点发送 **POST** 请求。`/two-factor-challenge` 动作需要一个 `code` 字段，其中包含有效的 TOTP 令牌，或者一个 `recovery_code` 字段，其中包含用户的恢复码之一。

如果登录尝试成功，Fortify 会将用户重定向到通过应用 `fortify` 配置文件中的 `home` 配置选项设置的 URI。如果登录请求是 XHR 请求，则会返回 204 HTTP 响应。

如果请求不成功，用户将被重定向回双因素认证挑战页面，验证错误将通过共享的 `$errors` [Blade 模板变量](/docs/laravel/12.x/validation#quick-displaying-the-validation-errors) 提供给你。或者，在 XHR 请求的情况下，验证错误将随 422 HTTP 响应返回。

### 禁用双因素认证

要禁用双因素认证，你的应用应向 `/user/two-factor-authentication` 端点发送 **DELETE** 请求。请记住，Fortify 的双因素认证端点在调用前需要 [密码确认](#password-confirmation)。

## 注册

要开始实现应用的注册功能，我们需要告诉 Fortify 如何返回我们的“注册”视图。请记住，Fortify 是一个无前端（headless）的认证库。如果你想要一个已经完成前端实现的 Laravel 认证功能，你应该使用 [应用入门套件](/docs/laravel/12.x/starter-kits)。

Fortify 的所有视图渲染逻辑都可以通过 `Laravel\Fortify\Fortify` 类提供的相应方法进行自定义。通常，你应在 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用此方法：

```php
use Laravel\Fortify\Fortify;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    Fortify::registerView(function () {
        return view('auth.register');
    });

    // ...
}
```



Fortify 会负责定义返回该视图的 `/register` 路由。你的 `register` 模板应包含一个表单，该表单向 Fortify 定义的 `/register` 端点发送 **POST** 请求。

`/register` 端点需要以下字段：字符串类型的 `name`、字符串类型的邮箱地址或用户名、`password` 和 `password_confirmation`。邮箱/用户名字段的名称应与应用 `fortify` 配置文件中定义的 `username` 配置值匹配。

如果注册尝试成功，Fortify 会将用户重定向到通过应用 `fortify` 配置文件中的 `home` 配置选项设置的 URI。如果请求是 XHR 请求，将返回 201 HTTP 响应。

如果请求不成功，用户将被重定向回注册页面，验证错误将通过共享的 `$errors` [Blade 模板变量](/docs/laravel/12.x/validation#quick-displaying-the-validation-errors) 提供给你。或者，在 XHR 请求的情况下，验证错误将随 422 HTTP 响应返回。

### 自定义注册

用户验证和创建流程可以通过修改在安装 Laravel Fortify 时生成的 `App\Actions\Fortify\CreateNewUser` 动作来自定义。

## 密码重置

### 请求密码重置链接

要开始实现应用的密码重置功能，我们需要告诉 Fortify 如何返回“忘记密码”视图。请记住，Fortify 是一个无前端（headless）的认证库。如果你想要一个已经完成前端实现的 Laravel 认证功能，你应该使用 [应用入门套件](/docs/laravel/12.x/starter-kits)。



Fortify 的所有视图渲染逻辑都可以通过 `Laravel\Fortify\Fortify` 类提供的相应方法进行自定义。通常，你应在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用此方法：

```php
use Laravel\Fortify\Fortify;

/**
 * 启动任何应用服务。
 */
public function boot(): void
{
    Fortify::requestPasswordResetLinkView(function () {
        return view('auth.forgot-password');
    });

    // ...
}
```

Fortify 会负责定义返回该视图的 `/forgot-password` 端点。你的 `forgot-password` 模板应包含一个表单，该表单向 `/forgot-password` 端点发送 **POST** 请求。

`/forgot-password` 端点需要一个字符串类型的 `email` 字段。该字段名或数据库列名应与应用 `fortify` 配置文件中的 `email` 配置值匹配。

#### 处理密码重置链接请求的响应

如果密码重置链接请求成功，Fortify 会将用户重定向回 `/forgot-password` 端点，并向用户发送一封带有安全链接的邮件，该链接可用于重置密码。如果请求是 XHR 请求，将返回 200 HTTP 响应。

在成功请求后被重定向回 `/forgot-password` 端点后，可以使用 `status` 会话变量来显示密码重置链接请求的状态。

`$status` 会话变量的值将与应用的 `passwords` [语言文件](/docs/laravel/12.x/localization)中定义的某个翻译字符串匹配。如果你希望自定义此值，并且尚未发布 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令进行：

```html
@if (session('status'))
    <div class="mb-4 font-medium text-sm text-green-600">
        {{ session('status') }}
    </div>
@endif
```



如果请求不成功，用户将被重定向回“请求密码重置链接”页面，验证错误将通过共享的 `$errors` [Blade 模板变量](/docs/laravel/12.x/validation#quick-displaying-the-validation-errors) 提供给你。或者，在 XHR 请求的情况下，验证错误将随 422 HTTP 响应返回。

### 重置密码

要完成应用的密码重置功能，我们需要告诉 Fortify 如何返回“重置密码”视图。

Fortify 的所有视图渲染逻辑都可以通过 `Laravel\Fortify\Fortify` 类提供的相应方法进行自定义。通常，你应在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用此方法：

```php
use Laravel\Fortify\Fortify;
use Illuminate\Http\Request;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    Fortify::resetPasswordView(function (Request $request) {
        return view('auth.reset-password', ['request' => $request]);
    });

    // ...
}
```

Fortify 会负责定义显示该视图的路由。你的 `reset-password` 模板应包含一个表单，该表单向 `/reset-password` 发送 **POST** 请求。

`/reset-password` 端点需要以下字段：字符串类型的 `email`、`password`、`password_confirmation`，以及一个名为 `token` 的隐藏字段，其值为 `request()->route('token')`。邮箱字段名或数据库列名应与应用 `fortify` 配置文件中定义的 `email` 配置值匹配。

#### 处理密码重置响应

如果密码重置请求成功，Fortify 会将用户重定向回 `/login` 路由，以便用户使用新密码登录。此外，将设置一个 `status` 会话变量，以便你在登录页面显示重置成功的状态：

```blade
@if (session('status'))
    <div class="mb-4 font-medium text-sm text-green-600">
        {{ session('status') }}
    </div>
@endif
```



如果请求是 XHR 请求，将返回 200 HTTP 响应。

如果请求不成功，用户将被重定向回“重置密码”页面，验证错误将通过共享的 `$errors` [Blade 模板变量](/docs/laravel/12.x/validation#quick-displaying-the-validation-errors) 提供给你。或者，在 XHR 请求的情况下，验证错误将随 422 HTTP 响应返回。

### 自定义密码重置

密码重置流程可以通过修改在安装 Laravel Fortify 时生成的 `App\Actions\ResetUserPassword` 动作进行自定义。

## 邮箱验证

注册后，你可能希望用户在继续访问应用之前验证他们的邮箱地址。要开始，请确保在 `fortify` 配置文件的 `features` 数组中启用了 `emailVerification` 功能。接下来，应确保你的 `App\Models\User` 类实现了 `Illuminate\Contracts\Auth\MustVerifyEmail` 接口。

完成这两个设置步骤后，新注册的用户将收到一封邮件，提示他们验证邮箱所有权。然而，我们需要告诉 Fortify 如何显示邮箱验证界面，该界面告知用户需要点击邮件中的验证链接。

Fortify 的所有视图渲染逻辑都可以通过 `Laravel\Fortify\Fortify` 类提供的相应方法进行自定义。通常，你应在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用此方法：

```php
use Laravel\Fortify\Fortify;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    Fortify::verifyEmailView(function () {
        return view('auth.verify-email');
    });

    // ...
}
```



Fortify 会负责定义显示该视图的路由，当用户被 Laravel 内置的 `verified` 中间件重定向到 `/email/verify` 端点时，该视图会被显示。

你的 `verify-email` 模板应包含一条提示信息，告知用户点击发送到其邮箱的验证链接。

#### 重新发送邮箱验证链接

如果需要，你可以在应用的 `verify-email` 模板中添加一个按钮，该按钮触发 **POST** 请求到 `/email/verification-notification` 端点。当该端点收到请求时，会向用户发送一封新的验证邮件链接，允许用户在之前的链接意外删除或丢失时获取新的验证链接。

如果重新发送验证链接邮件请求成功，Fortify 会将用户重定向回 `/email/verify` 端点，并设置 `status` 会话变量，从而可以向用户显示操作成功的信息。如果请求是 XHR 请求，将返回 202 HTTP 响应：

```blade
@if (session('status') == 'verification-link-sent')
    <div class="mb-4 font-medium text-sm text-green-600">
        A new email verification link has been emailed to you!
    </div>
@endif
```

### 保护路由

要指定某个路由或路由组需要用户已验证邮箱地址，应将 Laravel 内置的 `verified` 中间件附加到该路由。`verified` 中间件别名由 Laravel 自动注册，用作 `Illuminate\Auth\Middleware\EnsureEmailIsVerified` 中间件的别名：

```php
Route::get('/dashboard', function () {
    // ...
})->middleware(['verified']);
```



## 密码确认

在构建应用程序时，你可能会遇到某些操作需要用户在执行之前确认他们的密码。通常，这些路由由 Laravel 内置的 `password.confirm` 中间件保护。

要开始实现密码确认功能，我们需要告诉 Fortify 如何返回应用的“密码确认”视图。请记住，Fortify 是一个无前端（headless）的认证库。如果你希望使用已经完成前端实现的 Laravel 认证功能，你应该使用 [应用入门套件](/docs/laravel/12.x/starter-kits)。

Fortify 的所有视图渲染逻辑都可以通过 `Laravel\Fortify\Fortify` 类提供的相应方法进行自定义。通常，你应在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用此方法：

```php
use Laravel\Fortify\Fortify;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    Fortify::confirmPasswordView(function () {
        return view('auth.confirm-password');
    });

    // ...
}
```

Fortify 会负责定义返回该视图的 `/user/confirm-password` 端点。你的 `confirm-password` 模板应包含一个表单，该表单向 `/user/confirm-password` 端点发送 **POST** 请求。`/user/confirm-password` 端点需要一个 `password` 字段，其中包含用户当前的密码。

如果密码与用户当前密码匹配，Fortify 会将用户重定向到他们尝试访问的路由。如果请求是 XHR 请求，将返回 201 HTTP 响应。

如果请求不成功，用户将被重定向回密码确认页面，验证错误将通过共享的 `$errors` Blade 模板变量提供给你。或者，在 XHR 请求的情况下，验证错误将随 422 HTTP 响应返回。
