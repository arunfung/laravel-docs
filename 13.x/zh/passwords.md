# 重置密码

- [简介](#introduction)
    - [配置](#configuration)
    - [驱动使用前提](#driver-prerequisites)
    - [模型准备](#model-preparation)
    - [配置受信任主机](#configuring-trusted-hosts)
- [路由](#routing)
    - [请求密码重置链接](#requesting-the-password-reset-link)
    - [重置密码](#resetting-the-password)
- [删除过期令牌](#deleting-expired-tokens)
- [自定义](#password-customization)

<a name="introduction"></a>
## 简介

大多数 Web 应用都允许用户重置忘记的密码。Laravel 提供了便捷的服务，用于发送密码重置链接和安全地重置密码，让你无需在每个新应用中手动实现这项功能。

> [!NOTE]
> 想要快速上手？在全新的 Laravel 应用中安装一个 Laravel [应用入门套件](/docs/{{version}}/starter-kits)。入门套件会为你搭建完整的身份认证系统，包括忘记密码后的重置功能。

<a name="configuration"></a>
### 配置

应用的密码重置配置位于 `config/auth.php` 文件中，请仔细查看其中的配置选项。默认情况下，Laravel 使用 `database` 密码重置驱动。

密码重置的 `driver` 配置项决定密码重置数据的存储位置。Laravel 提供了两种驱动：

<div class="content-list" markdown="1">

- `database` - 将密码重置数据存储在关系型数据库中。
- `cache` - 将密码重置数据存储在某个缓存存储中。

</div>

<a name="driver-prerequisites"></a>
### 驱动使用前提

<a name="database"></a>
#### 数据库

使用默认的 `database` 驱动时，必须创建一张表来存储应用的密码重置令牌。Laravel 默认的 `0001_01_01_000000_create_users_table.php` 数据库迁移通常已经包含这张表。

<a name="cache"></a>
#### 缓存

也可以使用缓存驱动处理密码重置，这种方式无需专门的数据库表。缓存条目以用户邮箱地址的 SHA-256 哈希值作为键：

```php
'passwords' => [
    'users' => [
        'driver' => 'cache',
        'provider' => 'users',
        'store' => 'passwords', // 可选……
        'expire' => 60,
        'throttle' => 60,
    ],
],
```

为避免调用 `artisan cache:clear` 时清除密码重置数据，可以通过 `store` 配置项指定一个独立的缓存存储。这个值应对应 `config/cache.php` 配置文件中定义的某个存储。

<a name="model-preparation"></a>
### 模型准备

使用 Laravel 的密码重置功能之前，应用的 `App\Models\User` 模型必须使用 `Illuminate\Notifications\Notifiable` trait。新 Laravel 应用中创建的默认 `App\Models\User` 模型通常已经包含这个 trait。

接下来，请确认 `App\Models\User` 模型实现了 `Illuminate\Contracts\Auth\CanResetPassword` 接口。框架自带的 `App\Models\User` 模型已经实现这个接口，并通过 `Illuminate\Auth\Passwords\CanResetPassword` trait 引入实现接口所需的方法。

<a name="configuring-trusted-hosts"></a>
### 配置受信任主机

默认情况下，无论 HTTP 请求的 `Host` 请求头内容如何，Laravel 都会响应收到的所有请求。此外，在 Web 请求期间生成指向应用的绝对 URL 时，也会使用 `Host` 请求头的值。

通常，应配置 Nginx 或 Apache 等 Web 服务器，只将匹配指定主机名的请求转发给应用。如果无法直接自定义 Web 服务器，又需要让 Laravel 只响应特定主机名的请求，可以在应用的 `bootstrap/app.php` 文件中使用 `trustHosts` 中间件方法。当应用提供密码重置功能时，这一点尤其重要。

有关这个中间件方法的更多信息，请参阅 [TrustHosts 中间件文档](/docs/{{version}}/requests#configuring-trusted-hosts)。

<a name="routing"></a>
## 路由

要完整实现密码重置功能，需要定义几条路由。首先，需要一对路由，让用户通过邮箱地址请求密码重置链接。其次，还需要一对路由，在用户访问邮件中的密码重置链接并填写密码重置表单后，完成密码重置。

<a name="requesting-the-password-reset-link"></a>
### 请求密码重置链接

<a name="the-password-reset-link-request-form"></a>
#### 密码重置链接请求表单

首先，定义请求密码重置链接所需的路由。从下面这条路由开始，它会返回包含密码重置链接请求表单的视图：

```php
Route::get('/forgot-password', function () {
    return view('auth.forgot-password');
})->middleware('guest')->name('password.request');
```

这个路由返回的视图应包含一个带有 `email` 字段的表单，让用户为指定邮箱地址请求密码重置链接。

<a name="password-reset-link-handling-the-form-submission"></a>
#### 处理表单提交

接下来，定义一条路由，处理「忘记密码」视图发出的表单提交请求。这个路由负责验证邮箱地址，并向对应的用户发送密码重置请求：

```php
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Password;

Route::post('/forgot-password', function (Request $request) {
    $request->validate(['email' => 'required|email']);

    $status = Password::sendResetLink(
        $request->only('email')
    );

    return $status === Password::ResetLinkSent
        ? back()->with(['status' => __($status)])
        : back()->withErrors(['email' => __($status)]);
})->middleware('guest')->name('password.email');
```

继续之前，我们先仔细看看这个路由。首先，验证请求的 `email` 属性。接着，通过 `Password` 门面使用 Laravel 内置的「密码代理」向用户发送密码重置链接。密码代理会根据给定字段（这里是邮箱地址）查找用户，再通过 Laravel 内置的 [通知系统](/docs/{{version}}/notifications) 向用户发送密码重置链接。

`sendResetLink` 方法会返回一个「状态」标识符。可以使用 Laravel 的 [本地化](/docs/{{version}}/localization) 辅助函数翻译这个状态，向用户显示易于理解的请求状态消息。密码重置状态的译文由应用的 `lang/{lang}/passwords.php` 语言文件决定。`passwords` 语言文件为状态标识符的每个可能值都提供了对应的条目。

> [!NOTE]
> 默认情况下，Laravel 应用骨架不包含 `lang` 目录。如果希望自定义 Laravel 的语言文件，可以通过 `lang:publish` Artisan 命令发布这些文件。

你可能想知道，调用 `Password` 门面的 `sendResetLink` 方法时，Laravel 如何从应用的数据库中查找用户记录。Laravel 的密码代理会利用身份认证系统的「用户提供者」来获取数据库记录。密码代理使用的用户提供者在 `config/auth.php` 配置文件的 `passwords` 配置数组中指定。有关编写自定义用户提供者的更多信息，请参阅 [身份认证文档](/docs/{{version}}/authentication#adding-custom-user-providers)。

> [!NOTE]
> 手动实现密码重置功能时，需要自行定义视图和路由。如果希望直接生成包含所有必要身份认证和验证逻辑的应用骨架，请参阅 [Laravel 应用入门套件](/docs/{{version}}/starter-kits)。

<a name="resetting-the-password"></a>
### 重置密码

<a name="the-password-reset-form"></a>
#### 密码重置表单

接下来，定义完成密码重置所需的路由，处理用户点击邮件中的密码重置链接并提供新密码的流程。首先，定义一条路由，在用户点击密码重置链接时显示重置密码表单。这个路由会接收一个 `token` 参数，稍后将用它验证密码重置请求：

```php
Route::get('/reset-password/{token}', function (string $token) {
    return view('auth.reset-password', ['token' => $token]);
})->middleware('guest')->name('password.reset');
```

这个路由返回的视图应显示一个表单，包含 `email`、`password`、`password_confirmation` 字段，以及隐藏的 `token` 字段。`token` 字段的值应为路由接收到的秘密令牌 `$token`。

<a name="password-reset-handling-the-form-submission"></a>
#### 处理表单提交

还需要定义一条路由，处理密码重置表单的提交。这个路由负责验证传入请求，并更新数据库中的用户密码：

```php
use App\Models\User;
use Illuminate\Auth\Events\PasswordReset;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Password;
use Illuminate\Support\Str;

Route::post('/reset-password', function (Request $request) {
    $request->validate([
        'token' => 'required',
        'email' => 'required|email',
        'password' => 'required|min:8|confirmed',
    ]);

    $status = Password::reset(
        $request->only('email', 'password', 'password_confirmation', 'token'),
        function (User $user, string $password) {
            $user->forceFill([
                'password' => Hash::make($password)
            ])->setRememberToken(Str::random(60));

            $user->save();

            event(new PasswordReset($user));
        }
    );

    return $status === Password::PasswordReset
        ? redirect()->route('login')->with('status', __($status))
        : back()->withErrors(['email' => [__($status)]]);
})->middleware('guest')->name('password.update');
```

继续之前，我们先仔细看看这个路由。首先，验证请求的 `token`、`email` 和 `password` 属性。接着，通过 `Password` 门面使用 Laravel 内置的「密码代理」，验证密码重置请求中的凭据。

如果传给密码代理的令牌、邮箱地址和密码有效，就会调用传给 `reset` 方法的闭包。这个闭包会接收用户实例，以及用户在密码重置表单中提供的明文密码。我们可以在闭包中更新数据库里的用户密码。

`reset` 方法会返回一个「状态」标识符。可以使用 Laravel 的 [本地化](/docs/{{version}}/localization) 辅助函数翻译这个状态，向用户显示易于理解的请求状态消息。密码重置状态的译文由应用的 `lang/{lang}/passwords.php` 语言文件决定。`passwords` 语言文件为状态标识符的每个可能值都提供了对应的条目。如果应用不包含 `lang` 目录，可以使用 `lang:publish` Artisan 命令创建它。

继续之前，你可能想知道，调用 `Password` 门面的 `reset` 方法时，Laravel 如何从应用的数据库中查找用户记录。Laravel 的密码代理会利用身份认证系统的「用户提供者」来获取数据库记录。密码代理使用的用户提供者在 `config/auth.php` 配置文件的 `passwords` 配置数组中指定。有关编写自定义用户提供者的更多信息，请参阅 [身份认证文档](/docs/{{version}}/authentication#adding-custom-user-providers)。

<a name="deleting-expired-tokens"></a>
## 删除过期令牌

使用 `database` 驱动时，已过期的密码重置令牌仍会保留在数据库中。不过，可以使用 `auth:clear-resets` Artisan 命令轻松删除这些记录：

```shell
php artisan auth:clear-resets
```

如果希望自动执行这项清理，可以将命令添加到应用的 [调度器](/docs/{{version}}/scheduling) 中：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('auth:clear-resets')->everyFifteenMinutes();
```

<a name="password-customization"></a>
## 自定义

<a name="reset-link-customization"></a>
#### 自定义重置链接

可以使用 `ResetPassword` 通知类提供的 `createUrlUsing` 方法，自定义密码重置链接的 URL。这个方法接收一个闭包，闭包会接收通知的目标用户实例和密码重置链接令牌。通常，应在应用的 `AppServiceProvider` 的 `boot` 方法中调用这个方法：

```php
use App\Models\User;
use Illuminate\Auth\Notifications\ResetPassword;

/**
 * 初始化应用服务。
 */
public function boot(): void
{
    ResetPassword::createUrlUsing(function (User $user, string $token) {
        return 'https://example.com/reset-password?token='.$token;
    });
}
```

<a name="reset-email-customization"></a>
#### 自定义重置邮件

你可以轻松更换向用户发送密码重置链接时使用的通知类。首先，重写 `App\Models\User` 模型的 `sendPasswordResetNotification` 方法。在这个方法中，可以使用任何自行创建的 [通知类](/docs/{{version}}/notifications) 发送通知。密码重置令牌 `$token` 是这个方法接收的第一个参数。可以用它构建自定义的密码重置 URL，再向用户发送通知：

```php
use App\Notifications\ResetPasswordNotification;

/**
 * 向用户发送密码重置通知。
 *
 * @param  string  $token
 */
public function sendPasswordResetNotification($token): void
{
    $url = 'https://example.com/reset-password?token='.$token;

    $this->notify(new ResetPasswordNotification($url));
}
```
