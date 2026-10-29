# Laravel Fortify

- [简介](#introduction)
    - [什么是 Fortify？](#what-is-fortify)
    - [何时使用 Fortify？](#when-should-i-use-fortify)
- [安装](#installation)
    - [Fortify 功能](#fortify-features)
    - [禁用视图](#disabling-views)
- [身份认证](#authentication)
    - [自定义用户认证](#customizing-user-authentication)
    - [自定义认证管道](#customizing-the-authentication-pipeline)
    - [自定义重定向](#customizing-authentication-redirects)
- [双因素认证](#two-factor-authentication)
    - [启用双因素认证](#enabling-two-factor-authentication)
    - [使用双因素认证登录](#authenticating-with-two-factor-authentication)
    - [禁用双因素认证](#disabling-two-factor-authentication)
- [通行密钥](#passkeys)
    - [启用通行密钥](#enabling-passkeys)
    - [JavaScript 客户端](#passkeys-javascript-client)
    - [使用通行密钥认证](#authenticating-with-passkeys)
    - [使用通行密钥确认密码](#confirming-password-with-passkeys)
    - [注册通行密钥](#registering-passkeys)
    - [删除通行密钥](#deleting-passkeys)
- [注册](#registration)
    - [自定义注册](#customizing-registration)
- [重置密码](#password-reset)
    - [请求密码重置链接](#requesting-a-password-reset-link)
    - [重置密码](#resetting-the-password)
    - [自定义密码重置](#customizing-password-resets)
- [邮箱验证](#email-verification)
    - [保护路由](#protecting-routes)
- [密码确认](#password-confirmation)

<a name="introduction"></a>
## 简介

[Laravel Fortify](https://github.com/laravel/fortify) 是 Laravel 中与前端无关的身份认证后端实现。Fortify 注册了实现 Laravel 全部认证功能所需的路由和控制器，包括登录、注册、密码重置和邮箱验证等。安装 Fortify 后，你可以运行 `route:list` Artisan 命令查看它注册的路由。

由于 Fortify 不提供用户界面，你需要搭配自己的界面使用，并向它注册的路由发送请求。本文后续将详细介绍如何向这些路由发送请求。

> [!NOTE]
> Fortify 是一个帮助你快速实现 Laravel 认证功能的扩展包。**你并非必须使用它。** 你也可以按照[身份认证](/docs/{{version}}/authentication)、[密码重置](/docs/{{version}}/passwords)和[邮箱验证](/docs/{{version}}/verification)文档，手动使用 Laravel 的认证服务。

<a name="what-is-fortify"></a>
### 什么是 Fortify？

如前所述，Laravel Fortify 是 Laravel 中与前端无关的身份认证后端实现。Fortify 注册了实现 Laravel 全部认证功能所需的路由和控制器，包括登录、注册、密码重置和邮箱验证等。

**使用 Laravel 的认证功能并不要求使用 Fortify。** 你也可以按照[身份认证](/docs/{{version}}/authentication)、[密码重置](/docs/{{version}}/passwords)和[邮箱验证](/docs/{{version}}/verification)文档，手动使用 Laravel 的认证服务。

如果你刚接触 Laravel，不妨了解一下[应用入门套件](/docs/{{version}}/starter-kits)。Laravel 的应用入门套件在内部使用 Fortify 为应用提供认证脚手架，并包含使用 [Tailwind CSS](https://tailwindcss.com) 构建的用户界面，方便你学习并熟悉 Laravel 的认证功能。

Laravel Fortify 本质上将应用入门套件的路由和控制器封装为一个不含用户界面的扩展包，让你可以快速搭建应用认证层的后端实现，同时不受特定前端方案的限制。

<a name="when-should-i-use-fortify"></a>
### 何时使用 Fortify？

你可能想知道什么时候适合使用 Laravel Fortify。首先，如果你使用了 Laravel 的[应用入门套件](/docs/{{version}}/starter-kits)，就无需安装 Laravel Fortify，因为所有入门套件都使用 Fortify，并已提供完整的认证实现。

如果你没有使用应用入门套件，而应用需要认证功能，可以选择手动实现这些功能，或使用 Laravel Fortify 提供其后端实现。

如果选择安装 Fortify，用户界面将向本文介绍的 Fortify 认证路由发送请求，以认证和注册用户。

如果选择不使用 Fortify，而是手动使用 Laravel 的认证服务，可以参考[身份认证](/docs/{{version}}/authentication)、[密码重置](/docs/{{version}}/passwords)和[邮箱验证](/docs/{{version}}/verification)文档。

<a name="laravel-fortify-and-laravel-sanctum"></a>
#### Laravel Fortify 与 Laravel Sanctum

一些开发者对 [Laravel Sanctum](/docs/{{version}}/sanctum) 和 Laravel Fortify 的区别感到困惑。这两个扩展包解决的是不同但相关的问题，因此它们并不互斥，也不是竞争关系。

Laravel Sanctum 只负责管理 API 令牌，以及使用会话 Cookie 或令牌对已有用户进行认证。Sanctum 不提供处理用户注册、密码重置等功能的路由。

如果你正在为提供 API 或作为单页应用后端的应用手动构建认证层，完全可以同时使用 Laravel Fortify（处理用户注册、密码重置等）和 Laravel Sanctum（管理 API 令牌和进行会话认证）。

<a name="installation"></a>
## 安装

首先，使用 Composer 包管理器安装 Fortify：

```shell
composer require laravel/fortify
```

接下来，使用 `fortify:install` Artisan 命令发布 Fortify 的资源：

```shell
php artisan fortify:install
```

该命令会将 Fortify 的动作类发布到 `app/Actions` 目录；如果目录不存在，将自动创建。此外，还会发布 `FortifyServiceProvider`、配置文件和所有必需的数据库迁移。

接下来，运行数据库迁移：

```shell
php artisan migrate
```

<a name="fortify-features"></a>
### Fortify 功能

`fortify` 配置文件包含一个 `features` 配置数组，用于定义 Fortify 默认暴露哪些后端路由和功能。我们建议只启用以下功能，这些是大多数 Laravel 应用提供的基本认证功能：

```php
'features' => [
    Features::registration(),
    Features::resetPasswords(),
    Features::emailVerification(),
],
```

<a name="disabling-views"></a>
### 禁用视图

默认情况下，Fortify 定义了一些用于返回视图的路由，例如登录页或注册页。如果你正在构建由 JavaScript 驱动的单页应用，可能不需要这些路由。此时，可以将应用 `config/fortify.php` 配置文件中的 `views` 设为 `false`，完全禁用这些路由：

```php
'views' => false,
```

<a name="disabling-views-and-password-reset"></a>
#### 禁用视图与密码重置

如果你禁用了 Fortify 的视图，并打算为应用实现密码重置功能，仍需定义一个名为 `password.reset` 的路由，用于显示应用的「重置密码」视图。这是因为 Laravel 的 `Illuminate\Auth\Notifications\ResetPassword` 通知会通过名为 `password.reset` 的路由生成密码重置 URL。

<a name="authentication"></a>
## 身份认证

首先，我们需要告诉 Fortify 如何返回「登录」视图。Fortify 是一个无界面的认证库。如果希望使用已经实现好的 Laravel 认证前端，可以使用[应用入门套件](/docs/{{version}}/starter-kits)。

你可以使用 `Laravel\Fortify\Fortify` 类提供的相应方法，自定义所有认证视图的渲染逻辑。通常，应在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用该方法。Fortify 会负责定义返回此视图的 `/login` 路由：

```php
use Laravel\Fortify\Fortify;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Fortify::loginView(function () {
        return view('auth.login');
    });

    // ...
}
```

登录模板应包含一个向 `/login` 发送 POST 请求的表单。`/login` 端点需要字符串类型的 `email` / `username` 和 `password`。邮箱或用户名字段的名称应与 `config/fortify.php` 配置文件中的 `username` 值一致。此外，可以提供布尔型 `remember` 字段，表示用户希望使用 Laravel 提供的「记住我」功能。

如果登录成功，Fortify 会将用户重定向到应用 `fortify` 配置文件中 `home` 选项指定的 URI。如果登录请求是 XHR 请求，则返回 200 HTTP 响应。

如果请求失败，用户将被重定向回登录页面，你可以通过共享的 `$errors` [Blade 模板变量](/docs/{{version}}/validation#quick-displaying-the-validation-errors)获取验证错误。如果是 XHR 请求，验证错误将随 422 HTTP 响应返回。

<a name="customizing-user-authentication"></a>
### 自定义用户认证

Fortify 会根据提供的凭证和应用配置的认证守卫，自动查找并认证用户。有时，你可能希望完全自定义登录凭证的验证方式和用户的查找方式。Fortify 的 `Fortify::authenticateUsing` 方法可以方便地实现这一需求。

该方法接受一个接收传入 HTTP 请求的闭包。闭包负责验证请求中携带的登录凭证，并返回对应的用户实例。如果凭证无效或找不到用户，闭包应返回 `null` 或 `false`。通常，应在 `FortifyServiceProvider` 的 `boot` 方法中调用该方法：

```php
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Laravel\Fortify\Fortify;

/**
 * 引导应用服务。
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

<a name="authentication-guard"></a>
#### 认证守卫

你可以在应用的 `fortify` 配置文件中自定义 Fortify 使用的认证守卫，但应确保所配置的守卫实现了 `Illuminate\Contracts\Auth\StatefulGuard`。如果使用 Laravel Fortify 为单页应用进行认证，应结合 [Laravel Sanctum](https://laravel.com/docs/sanctum) 使用 Laravel 默认的 `web` 守卫。

<a name="customizing-the-authentication-pipeline"></a>
### 自定义认证管道

Laravel Fortify 通过由可调用类组成的管道认证登录请求。你可以自定义登录请求经过的类管道。每个类都应包含一个 `__invoke` 方法，接收传入的 `Illuminate\Http\Request` 实例，并像[中间件](/docs/{{version}}/middleware)一样接收 `$next` 变量，调用它即可将请求传递给管道中的下一个类。

你可以使用 `Fortify::authenticateThrough` 方法定义自定义管道。该方法接受一个闭包，闭包应返回登录请求需要经过的类数组。通常，应在 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用该方法。

以下示例包含默认管道定义，你可以在此基础上进行修改：

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

#### 认证限流

默认情况下，Fortify 使用 `EnsureLoginIsNotThrottled` 中间件限制认证尝试次数。该中间件按用户名与 IP 地址的组合进行限流。

有些应用可能需要不同的认证限流方式，例如仅按 IP 地址限流。因此，Fortify 允许你通过 `fortify.limiters.login` 配置选项指定自己的[速率限制器](/docs/{{version}}/routing#rate-limiting)。该选项位于应用的 `config/fortify.php` 配置文件中。

> [!NOTE]
> 综合使用限流、[双因素认证](/docs/{{version}}/fortify#two-factor-authentication)和外部 Web 应用防火墙（WAF），可以为应用的合法用户提供最可靠的保护。

<a name="customizing-authentication-redirects"></a>
### 自定义重定向

如果登录成功，Fortify 会将用户重定向到应用 `fortify` 配置文件中 `home` 选项指定的 URI。如果登录请求是 XHR 请求，则返回 200 HTTP 响应。用户退出登录后，将被重定向到 `/` URI。

如果需要进一步自定义此行为，可以将 `LoginResponse` 和 `LogoutResponse` 契约的实现绑定到 Laravel [服务容器](/docs/{{version}}/container)。通常应在应用的 `App\Providers\FortifyServiceProvider` 类的 `register` 方法中完成：

```php
use Laravel\Fortify\Contracts\LogoutResponse;

/**
 * 注册应用服务。
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

<a name="two-factor-authentication"></a>
## 双因素认证

启用 Fortify 的双因素认证后，用户在认证过程中需要输入六位数字令牌。该令牌通过基于时间的一次性密码（TOTP）生成，可以从任何兼容 TOTP 的移动认证应用中获取，例如 Google Authenticator。

开始之前，应先确保应用的 `App\Models\User` 模型使用了 `Laravel\Fortify\TwoFactorAuthenticatable` trait：

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

接下来，应在应用中创建一个供用户管理双因素认证设置的页面。该页面应允许用户启用和禁用双因素认证，以及重新生成双因素认证恢复码。

> 默认情况下，`fortify` 配置文件中的 `features` 数组要求用户在修改双因素认证设置前确认密码。因此，继续之前，应用应先实现 Fortify 的[密码确认](#password-confirmation)功能。

<a name="enabling-two-factor-authentication"></a>
### 启用双因素认证

要开始启用双因素认证，应用应向 Fortify 定义的 `/user/two-factor-authentication` 端点发送 POST 请求。请求成功后，用户将被重定向回先前的 URL，会话变量 `status` 将被设为 `two-factor-authentication-enabled`。你可以在模板中检查该 `status` 会话变量，以显示相应的成功消息。如果请求是 XHR 请求，则返回 `200` HTTP 响应。

选择启用双因素认证后，用户仍须提供有效的双因素认证码来「确认」配置。因此，「成功」消息应提示用户仍需确认双因素认证：

```html
@if (session('status') == 'two-factor-authentication-enabled')
    <div class="mb-4 font-medium text-sm">
        Please finish configuring two-factor authentication below.
    </div>
@endif
```

接下来，应显示双因素认证二维码，让用户使用认证应用扫描。如果使用 Blade 渲染应用前端，可以通过用户实例的 `twoFactorQrCodeSvg` 方法获取二维码 SVG：

```php
$request->user()->twoFactorQrCodeSvg();
```

如果你正在构建 JavaScript 前端，可以向 `/user/two-factor-qr-code` 端点发送 XHR GET 请求，获取用户的双因素认证二维码。该端点返回包含 `svg` 键的 JSON 对象。

<a name="confirming-two-factor-authentication"></a>
#### 确认双因素认证

除了显示用户的双因素认证二维码，还应提供文本输入框，让用户输入有效的认证码以「确认」双因素认证配置。该认证码应通过 POST 请求发送到 Fortify 定义的 `/user/confirmed-two-factor-authentication` 端点。

如果请求成功，用户将被重定向回先前的 URL，会话变量 `status` 将被设为 `two-factor-authentication-confirmed`：

```html
@if (session('status') == 'two-factor-authentication-confirmed')
    <div class="mb-4 font-medium text-sm">
        Two-factor authentication confirmed and enabled successfully.
    </div>
@endif
```

如果对双因素认证确认端点的请求是 XHR 请求，则返回 `200` HTTP 响应。

<a name="displaying-the-recovery-codes"></a>
#### 显示恢复码

你还应显示用户的双因素认证恢复码。如果用户无法使用移动设备，可以通过这些恢复码进行认证。如果使用 Blade 渲染应用前端，可以通过已认证的用户实例获取恢复码：

```php
(array) $request->user()->recoveryCodes();
```

如果你正在构建 JavaScript 前端，可以向 `/user/two-factor-recovery-codes` 端点发送 XHR GET 请求。该端点返回包含用户恢复码的 JSON 数组。

要重新生成用户的恢复码，应用应向 `/user/two-factor-recovery-codes` 端点发送 POST 请求。

<a name="authenticating-with-two-factor-authentication"></a>
### 使用双因素认证登录

认证过程中，Fortify 会自动将用户重定向到应用的双因素认证验证页面。如果应用发送的是 XHR 登录请求，认证成功后返回的 JSON 对象会包含布尔型 `two_factor` 属性。你应检查该值，判断是否需要重定向到双因素认证验证页面。

要实现双因素认证功能，首先需要告诉 Fortify 如何返回双因素认证验证视图。你可以使用 `Laravel\Fortify\Fortify` 类提供的相应方法自定义所有认证视图的渲染逻辑。通常，应在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用该方法：

```php
use Laravel\Fortify\Fortify;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Fortify::twoFactorChallengeView(function () {
        return view('auth.two-factor-challenge');
    });

    // ...
}
```

Fortify 会负责定义返回此视图的 `/two-factor-challenge` 路由。`two-factor-challenge` 模板应包含一个向 `/two-factor-challenge` 端点发送 POST 请求的表单。该操作需要包含有效 TOTP 令牌的 `code` 字段，或者包含用户恢复码的 `recovery_code` 字段。

如果登录成功，Fortify 会将用户重定向到应用 `fortify` 配置文件中 `home` 选项指定的 URI。如果登录请求是 XHR 请求，则返回 204 HTTP 响应。

如果请求失败，用户将被重定向回双因素认证验证页面，你可以通过共享的 `$errors` [Blade 模板变量](/docs/{{version}}/validation#quick-displaying-the-validation-errors)获取验证错误。如果是 XHR 请求，验证错误将随 422 HTTP 响应返回。

<a name="disabling-two-factor-authentication"></a>
### 禁用双因素认证

要禁用双因素认证，应用应向 `/user/two-factor-authentication` 端点发送 DELETE 请求。请注意，调用 Fortify 的双因素认证端点之前需要[确认密码](#password-confirmation)。

<a name="passkeys"></a>
## 通行密钥

Fortify 支持通过 WebAuthn 使用通行密钥进行认证。通行密钥允许用户使用 Face ID、Touch ID、Windows Hello 等平台认证器或硬件安全密钥，无需密码即可完成认证。

<a name="enabling-passkeys"></a>
### 启用通行密钥

首先，确保已在应用的 `fortify` 配置文件中启用 `passkeys` 功能：

```php
use Laravel\Fortify\Features;

'features' => [
    // ...
    Features::passkeys([
        'confirmPassword' => true,
    ]),
],
```

`confirmPassword` 选项决定 Fortify 是否要求用户在注册或删除通行密钥前[确认密码](#password-confirmation)。

接下来，确保应用的 `App\Models\User` 模型实现 `Laravel\Fortify\Contracts\PasskeyUser` 接口并使用 `Laravel\Fortify\PasskeyAuthenticatable` trait：

```php
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Fortify\Contracts\PasskeyUser;
use Laravel\Fortify\PasskeyAuthenticatable;

class User extends Authenticatable implements PasskeyUser
{
    use Notifiable, PasskeyAuthenticatable;
}
```

你可以通过应用的 `config/fortify.php` 文件中的 `passkeys` 配置数组自定义 Fortify 的通行密钥选项：

```php
'passkeys' => [
    'relying_party_id' => parse_url(config('app.url'), PHP_URL_HOST),
    'allowed_origins' => [config('app.url')],
    'user_handle_secret' => config('app.key'),
    'timeout' => 60000,
],
```

> [!NOTE]
> Fortify 封装了 `laravel/passkeys` Composer 扩展包并为你完成配置。如果使用 Fortify 的通行密钥功能，应在应用的 `config/fortify.php` 文件中配置通行密钥。你无需发布 `laravel/passkeys` 的配置文件，且其中定义的值会被 Fortify 覆盖。

`relying_party_id` 应与应用的域名一致。`allowed_origins` 数组列出了允许完成通行密钥注册和认证的浏览器来源。`user_handle_secret` 用于生成不透明的用户标识符，确保同一用户在多次注册通行密钥时能被识别。`timeout` 选项控制通行密钥注册和认证操作可保持活动的时长。

Fortify 对通行密钥登录、确认和注册路由使用专门的速率限制器。如有需要，你可以通过 `fortify.limiters.passkeys` 配置选项及对应的 `RateLimiter::for(...)` 定义进行自定义。

<a name="passkeys-javascript-client"></a>
### JavaScript 客户端

如果你正在构建自定义前端，包括使用浏览器端脚本的 Blade 应用，可以使用官方的 [`@laravel/passkeys`](https://www.npmjs.com/package/@laravel/passkeys) 扩展包。该包负责处理浏览器的 WebAuthn 交互流程，并向 Fortify 的通行密钥端点发送请求。

通过 npm 安装该包：

```shell
npm install @laravel/passkeys
```

然后，你可以从前端发起通行密钥注册和验证：

```js
import { Passkeys } from "@laravel/passkeys";

await Passkeys.register({ name: "MacBook Pro" });
await Passkeys.verify();
```

如果应用使用自定义通行密钥端点 URI，你可以在每次调用时覆盖路由：

```js
await Passkeys.verify({
    routes: {
        options: "/passkeys/confirm/options",
        submit: "/passkeys/confirm",
    },
});

await Passkeys.register({
    name: "MacBook Pro",
    routes: {
        options: "/user/passkeys/options",
        submit: "/user/passkeys",
    },
});
```

该包还通过 `@laravel/passkeys/react`、`@laravel/passkeys/vue` 和 `@laravel/passkeys/svelte` 提供 React、Vue 和 Svelte 辅助工具。

<a name="authenticating-with-passkeys"></a>
### 使用通行密钥认证

要使用通行密钥认证用户，应用应先向 `/passkeys/login/options` 端点发送 GET 请求。该端点返回 WebAuthn 质询选项，前端应将其传给 `navigator.credentials.get(...)`。

浏览器返回凭证后，应用应向 `/passkeys/login` 发送 POST 请求，并携带凭证数据。你也可以包含一个布尔型 `remember` 字段。

如果请求成功，Fortify 会通过配置的认证守卫登录用户，并返回：

<div class="content-list" markdown="1">

- 对于普通请求，返回重定向到预期目标的响应。
- 对于 XHR 请求，返回 `200` HTTP 响应，其 JSON 数据包含 `redirect` 键。

</div>

<a name="confirming-password-with-passkeys"></a>
### 使用通行密钥确认密码

对于已认证的会话，Fortify 提供通行密钥确认端点，以满足当前会话的 Laravel 密码确认要求。

要使用通行密钥确认身份，应用应先向 `/passkeys/confirm/options` 发送 GET 请求。该端点返回 WebAuthn 质询选项，前端应将其传给 `navigator.credentials.get(...)`。

浏览器返回凭证后，应用应向 `/passkeys/confirm` 发送 POST 请求，并携带凭证数据。

如果请求成功，Fortify 会将当前会话标记为已确认密码，并返回：

<div class="content-list" markdown="1">

- 对于普通请求，返回重定向到预期目标的响应。
- 对于 XHR 请求，返回 `200` HTTP 响应，其 JSON 数据包含 `redirect` 键。

</div>

<a name="registering-passkeys"></a>
### 注册通行密钥

要为已认证用户注册通行密钥，应用应先向 `/user/passkeys/options` 发送 GET 请求。该端点返回 WebAuthn 创建选项，前端应将其传给 `navigator.credentials.create(...)`。

浏览器返回凭证后，应用应向 `/user/passkeys` 发送 POST 请求，其中包含 `name` 字段和 `credential` 字段；后者包含 `navigator.credentials.create(...)` 返回的序列化 [`PublicKeyCredential`](https://developer.mozilla.org/en-US/docs/Web/API/PublicKeyCredential) 对象。

如果请求成功，Fortify 将返回：

<div class="content-list" markdown="1">

- 对于普通请求，返回重定向回上一页的响应，并在会话中设置 `passkey-registered` 状态。
- 返回 `200` HTTP 响应，其 JSON 数据包含 `status` 键以及新注册通行密钥的 `id` 和 `name`。

</div>

<a name="deleting-passkeys"></a>
### 删除通行密钥

要删除通行密钥，应用应向 `/user/passkeys/{passkey}` 发送 DELETE 请求。

如果请求成功，Fortify 将返回：

<div class="content-list" markdown="1">

- 对于普通请求，返回重定向回上一页的响应，并在会话中设置 `passkey-deleted` 状态。
- 对于 XHR 请求，返回 `200` HTTP 响应，其 JSON 数据包含 `status` 键。

</div>

<a name="registration"></a>
## 注册

要实现应用的注册功能，首先需要告诉 Fortify 如何返回「注册」视图。Fortify 是一个无界面的认证库。如果希望使用已经实现好的 Laravel 认证前端，可以使用[应用入门套件](/docs/{{version}}/starter-kits)。

你可以使用 `Laravel\Fortify\Fortify` 类提供的相应方法，自定义 Fortify 所有视图的渲染逻辑。通常，应在 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用该方法：

```php
use Laravel\Fortify\Fortify;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Fortify::registerView(function () {
        return view('auth.register');
    });

    // ...
}
```

Fortify 会负责定义返回此视图的 `/register` 路由。`register` 模板应包含一个向 Fortify 定义的 `/register` 端点发送 POST 请求的表单。

`/register` 端点需要字符串类型的 `name`、邮箱地址 / 用户名、`password` 和 `password_confirmation` 字段。邮箱或用户名字段的名称应与应用 `fortify` 配置文件中的 `username` 配置值一致。

如果注册成功，Fortify 会将用户重定向到应用 `fortify` 配置文件中 `home` 选项指定的 URI。如果请求是 XHR 请求，则返回 201 HTTP 响应。

如果请求失败，用户将被重定向回注册页面，你可以通过共享的 `$errors` [Blade 模板变量](/docs/{{version}}/validation#quick-displaying-the-validation-errors)获取验证错误。如果是 XHR 请求，验证错误将随 422 HTTP 响应返回。

<a name="customizing-registration"></a>
### 自定义注册

你可以修改安装 Laravel Fortify 时生成的 `App\Actions\Fortify\CreateNewUser` 动作类，自定义用户验证和创建过程。

<a name="password-reset"></a>
## 重置密码

<a name="requesting-a-password-reset-link"></a>
### 请求密码重置链接

要实现应用的密码重置功能，首先需要告诉 Fortify 如何返回「忘记密码」视图。Fortify 是一个无界面的认证库。如果希望使用已经实现好的 Laravel 认证前端，可以使用[应用入门套件](/docs/{{version}}/starter-kits)。

你可以使用 `Laravel\Fortify\Fortify` 类提供的相应方法，自定义 Fortify 所有视图的渲染逻辑。通常，应在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用该方法：

```php
use Laravel\Fortify\Fortify;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Fortify::requestPasswordResetLinkView(function () {
        return view('auth.forgot-password');
    });

    // ...
}
```

Fortify 会负责定义返回此视图的 `/forgot-password` 端点。`forgot-password` 模板应包含一个向 `/forgot-password` 端点发送 POST 请求的表单。

`/forgot-password` 端点需要字符串类型的 `email` 字段。该字段及数据库列的名称应与应用 `fortify` 配置文件中的 `email` 配置值一致。

<a name="handling-the-password-reset-link-request-response"></a>
#### 处理密码重置链接请求的响应

如果密码重置链接请求成功，Fortify 会将用户重定向回 `/forgot-password` 端点，并向用户发送包含安全密码重置链接的邮件。如果请求是 XHR 请求，则返回 200 HTTP 响应。

请求成功并重定向回 `/forgot-password` 端点后，可以使用 `status` 会话变量显示密码重置链接请求的状态。

`$status` 会话变量的值对应应用 `passwords` [语言文件](/docs/{{version}}/localization)中定义的翻译字符串之一。如果你希望自定义该值但尚未发布 Laravel 的语言文件，可以使用 `lang:publish` Artisan 命令发布：

```html
@if (session('status'))
    <div class="mb-4 font-medium text-sm text-green-600">
        {{ session('status') }}
    </div>
@endif
```

如果请求失败，用户将被重定向回请求密码重置链接的页面，你可以通过共享的 `$errors` [Blade 模板变量](/docs/{{version}}/validation#quick-displaying-the-validation-errors)获取验证错误。如果是 XHR 请求，验证错误将随 422 HTTP 响应返回。

<a name="resetting-the-password"></a>
### 重置密码

要完成应用的密码重置功能，还需要告诉 Fortify 如何返回「重置密码」视图。

你可以使用 `Laravel\Fortify\Fortify` 类提供的相应方法，自定义 Fortify 所有视图的渲染逻辑。通常，应在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用该方法：

```php
use Laravel\Fortify\Fortify;
use Illuminate\Http\Request;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Fortify::resetPasswordView(function (Request $request) {
        return view('auth.reset-password', ['request' => $request]);
    });

    // ...
}
```

Fortify 会负责定义显示此视图的路由。`reset-password` 模板应包含一个向 `/reset-password` 发送 POST 请求的表单。

`/reset-password` 端点需要字符串类型的 `email` 字段、`password` 字段、`password_confirmation` 字段，以及一个名为 `token` 的隐藏字段，其值为 `request()->route('token')`。「邮箱」字段及数据库列的名称应与应用 `fortify` 配置文件中的 `email` 配置值一致。

<a name="handling-the-password-reset-response"></a>
#### 处理密码重置响应

如果密码重置请求成功，Fortify 会重定向回 `/login` 路由，让用户使用新密码登录。此外，还会设置 `status` 会话变量，以便你在登录页面显示重置成功的状态：

```blade
@if (session('status'))
    <div class="mb-4 font-medium text-sm text-green-600">
        {{ session('status') }}
    </div>
@endif
```

如果请求是 XHR 请求，则返回 200 HTTP 响应。

如果请求失败，用户将被重定向回密码重置页面，你可以通过共享的 `$errors` [Blade 模板变量](/docs/{{version}}/validation#quick-displaying-the-validation-errors)获取验证错误。如果是 XHR 请求，验证错误将随 422 HTTP 响应返回。

<a name="customizing-password-resets"></a>
### 自定义密码重置

你可以修改安装 Laravel Fortify 时生成的 `App\Actions\Fortify\ResetUserPassword` 动作类，自定义密码重置过程。

<a name="email-verification"></a>
## 邮箱验证

注册后，你可能希望用户在继续访问应用之前验证邮箱地址。首先，确保已在 `fortify` 配置文件的 `features` 数组中启用 `emailVerification` 功能。接下来，确保 `App\Models\User` 类实现了 `Illuminate\Contracts\Auth\MustVerifyEmail` 接口。

完成这两项设置后，新注册的用户会收到一封邮件，提示他们验证邮箱地址的所有权。接下来，还需要告诉 Fortify 如何显示邮箱验证页面，提示用户点击邮件中的验证链接。

你可以使用 `Laravel\Fortify\Fortify` 类提供的相应方法，自定义 Fortify 所有视图的渲染逻辑。通常，应在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用该方法：

```php
use Laravel\Fortify\Fortify;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Fortify::verifyEmailView(function () {
        return view('auth.verify-email');
    });

    // ...
}
```

当 Laravel 内置的 `verified` 中间件将用户重定向到 `/email/verify` 端点时，Fortify 会负责定义显示此视图的路由。

`verify-email` 模板应包含提示消息，告知用户点击发送到其邮箱的验证链接。

<a name="resending-email-verification-links"></a>
#### 重新发送邮箱验证链接

你可以在应用的 `verify-email` 模板中添加一个按钮，触发向 `/email/verification-notification` 端点发送 POST 请求。该端点收到请求后，会向用户发送新的验证邮件，以便用户在之前的链接被误删或丢失时获取新链接。

如果重新发送验证邮件的请求成功，Fortify 会将用户重定向回 `/email/verify` 端点，并设置 `status` 会话变量，以便你向用户显示操作成功的提示。如果请求是 XHR 请求，则返回 202 HTTP 响应：

```blade
@if (session('status') == 'verification-link-sent')
    <div class="mb-4 font-medium text-sm text-green-600">
        A new email verification link has been emailed to you!
    </div>
@endif
```

<a name="protecting-routes"></a>
### 保护路由

要指定某个路由或路由组要求用户已验证邮箱地址，应为其附加 Laravel 内置的 `verified` 中间件。`verified` 中间件别名由 Laravel 自动注册，是 `Illuminate\Auth\Middleware\EnsureEmailIsVerified` 中间件的别名：

```php
Route::get('/dashboard', function () {
    // ...
})->middleware(['verified']);
```

<a name="password-confirmation"></a>
## 密码确认

构建应用时，有些操作可能需要用户先确认密码才能执行。通常，这些路由由 Laravel 内置的 `password.confirm` 中间件保护。

要实现密码确认功能，首先需要告诉 Fortify 如何返回应用的「密码确认」视图。Fortify 是一个无界面的认证库。如果希望使用已经实现好的 Laravel 认证前端，可以使用[应用入门套件](/docs/{{version}}/starter-kits)。

你可以使用 `Laravel\Fortify\Fortify` 类提供的相应方法，自定义 Fortify 所有视图的渲染逻辑。通常，应在应用的 `App\Providers\FortifyServiceProvider` 类的 `boot` 方法中调用该方法：

```php
use Laravel\Fortify\Fortify;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Fortify::confirmPasswordView(function () {
        return view('auth.confirm-password');
    });

    // ...
}
```

Fortify 会负责定义返回此视图的 `/user/confirm-password` 端点。`confirm-password` 模板应包含一个向该端点发送 POST 请求的表单。`/user/confirm-password` 端点需要一个包含用户当前密码的 `password` 字段。

如果密码与用户当前密码匹配，Fortify 会将用户重定向到他们原本尝试访问的路由。如果请求是 XHR 请求，则返回 201 HTTP 响应。

如果请求失败，用户将被重定向回密码确认页面，你可以通过共享的 `$errors` Blade 模板变量获取验证错误。如果是 XHR 请求，验证错误将随 422 HTTP 响应返回。
