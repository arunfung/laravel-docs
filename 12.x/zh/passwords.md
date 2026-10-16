
# 重置密码

-   [介绍](#introduction)
    -   [模型准备](#model-preparation)
    -   [数据库准备](#database-preparation)
    -   [配置受信任主机](#configuring-trusted-hosts)
-   [路由](#routing)
    -   [请求密码重置链接](#requesting-the-password-reset-link)
    -   [重置密码](#resetting-the-password)
-   [删除过期令牌](#deleting-expired-tokens)
-   [自定义](#password-customization)

## 介绍

大多数网页应用都会提供一种方式，让用户重置忘记的密码。
为了避免你在每个应用中都手动实现这一功能，Laravel 提供了方便的服务，用于发送密码重置链接和安全地重置密码。

> [!笔记]
> 想快速上手？可以在全新的 Laravel 应用中安装 Laravel [应用入门套件](/docs/laravel/12.x/starter-kits)。
Laravel 的入门套件会自动搭建完整的认证系统，包括忘记密码的重置功能。

### 模型准备

在使用 Laravel 的密码重置功能之前，你的应用 `App\Models\User` 模型必须使用 `Illuminate\Notifications\Notifiable` trait。
通常，新的 Laravel 应用创建的默认 `App\Models\User` 模型已经包含了这个 trait。

接下来，确认你的 `App\Models\User` 模型实现了 `Illuminate\Contracts\Auth\CanResetPassword` 接口。
框架自带的 `App\Models\User` 模型已经实现了该接口，并使用 `Illuminate\Auth\Passwords\CanResetPassword` trait 来包含实现接口所需的方法。

### 数据库准备

必须创建一个表来存储应用的密码重置令牌。
通常，这在 Laravel 默认的 `0001_01_01_000000_create_users_table.php` 数据库迁移中已经包含。

### 配置受信任主机



默认情况下，无论 HTTP 请求的 `Host` 标头内容如何，Laravel 都会响应它收到的所有请求。此外，在 Web 请求期间生成应用程序的绝对 URL 时，将使用 `Host` 标头的值。

通常，你应该配置你的 Web 服务器（例如 Nginx 或 Apache），使其仅将与给定主机名匹配的请求发送到你的应用程序。但是，如果你无法直接自定义 Web 服务器，并需要指示 Laravel 仅响应某些主机名，则可以通过在应用程序的 `bootstrap/app.php` 文件中使用 `trustHosts` 中间件方法来实现。当你的应用程序提供密码重置功能时，这一点尤其重要。

要了解有关此中间件方法的更多信息，请查阅 [TrustHosts 中间件文档](/docs/laravel/12.x/requests#configuring-trusted-hosts)。

<a name="routing"></a>
## 路由

为了正确实现允许用户重置密码的支持，我们需要定义几个路由。首先，我们需要一对路由来处理允许用户通过其电子邮件地址请求密码重置链接。其次，我们需要一对路由来处理用户访问通过电子邮件发送给他们的密码重置链接并完成密码重置表单后实际重置密码的操作。

<a name="requesting-the-password-reset-link"></a>
### 请求密码重置链接

<a name="the-password-reset-link-request-form"></a>
#### 密码重置链接请求表单

首先，我们将定义请求密码重置链接所需的路由。首先，我们将定义一个返回带有密码重置链接请求表单的视图的路由：

```php
Route::get('/forgot-password', function () {
    return view('auth.forgot-password');
})->middleware('guest')->name('password.request');
```


该路由返回的视图应包含一个 `email` 字段的表单，这个表单允许用户为给定的电子邮件地址请求密码重置链接。

#### 处理表单提交

接下来，我们将定义一个路由来处理来自“忘记密码”视图的表单提交请求。该路由负责验证电子邮件地址，并向对应的用户发送密码重置请求：

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

ible value of the status slug is located within the `passwords` language file.
在继续之前，让我们更详细地看看这个路由。首先，对请求中的 `email` 属性进行验证。
接着，我们将使用 Laravel 内置的“密码经纪人”（通过 `Password` facade）向用户发送密码重置链接。密码经纪人会负责根据给定字段（在本例中是电子邮件地址）检索用户，并通过 Laravel 内置的 [通知系统](/docs/laravel/12.x/notifications) 向用户发送密码重置链接。

`sendResetLink` 方法会返回一个“状态”标识。
可以使用 Laravel 的 [本地化](/docs/laravel/12.x/localization) 助手对该状态进行翻译，以向用户显示友好的请求状态消息。
密码重置状态的翻译由应用的 `lang/{lang}/passwords.php` 语言文件决定。该文件中为状态标识的每个可能值都提供了对应的条目。

> [!注意]
> 默认情况下，Laravel 应用模板并不包含 lang 目录。
如果你想自定义 Laravel 的语言文件，可以通过 lang:publish Artisan 命令发布它们。



你可能会想知道，当调用 `Password` facade 的 `sendResetLink` 方法时，Laravel 是如何知道从应用的数据库中检索用户记录的。Laravel 的密码经纪人会利用认证系统的“用户提供者”（user providers）来获取数据库记录。
密码经纪人使用的用户提供者在你的 `config/auth.php` 配置文件的 `passwords` 配置数组中进行配置。
想了解更多关于自定义用户提供者的内容，请查阅 [认证文档](/docs/laravel/12.x/authentication#adding-custom-user-providers)。

> [!注意]
> 当手动实现密码重置功能时，你需要自己定义视图和路由的内容。
如果你想使用包含所有必要认证和验证逻辑的脚手架，请查看 [Laravel 应用程序入门套件](/docs/laravel/12.x/starter-kits)。

### 重置密码

#### 密码重置表单

接下来，我们将定义实际重置密码所需的路由——当用户点击邮件中的密码重置链接并提供新密码时使用。
首先，定义显示重置密码表单的路由，该表单在用户点击重置密码链接时显示。该路由将接收一个 `token` 参数，我们稍后会使用它来验证密码重置请求：

```php
Route::get('/reset-password/{token}', function (string $token) {
    return view('auth.reset-password', ['token' => $token]);
})->middleware('guest')->name('password.reset');
```

此路由返回的视图应显示一个表单，表单包含：
-   一个 `email` 字段
-   一个 `password` 字段
-   一个 `password_confirmation` 字段
-   一个隐藏的 `token` 字段，其值应为路由接收到的 `$token`。



<a name="password-reset-handling-the-form-submission"></a>
#### 处理表单提交

当然，我们需要定义一个路由来实际处理密码重置表单提交。此路由将负责验证传入请求并在数据库中更新用户密码：

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

在继续之前，让我们详细检查此路由。首先，验证请求的 `token`、`email` 和 `password` 属性。接下来，我们将使用 Laravel 内置的「密码代理」（通过 `Password` 外观）来验证密码重置请求凭据。

如果提供给密码代理的令牌、电子邮件地址和密码有效，则将调用传递给 `reset` 方法的闭包。在此闭包中，它接收用户提供给密码重置表单的用户实例和明文密码，我们可以更新数据库中的用户密码。

`reset` 方法返回一个「状态」标识符。此状态可以使用 Laravel 的 [本地化](/docs/laravel/12.x/localization) 助手进行翻译，以便向用户显示关于其请求状态的用户友好消息。密码重置状态的翻译由应用程序的 `lang/{lang}/passwords.php` 语言文件确定。状态标识符的每个可能值在 `passwords` 语言文件中都有一个条目。如果您的应用程序不包含 `lang` 目录，您可以使用 `lang:publish` Artisan 命令创建它。



在继续之前，您可能想知道在调用 `Password` 外观的 `reset` 方法时，Laravel 是如何从应用程序数据库中检索用户记录的。Laravel 密码代理利用身份验证系统的「用户提供者」来检索数据库记录。密码代理使用的用户提供者在 `config/auth.php` 配置文件的 `passwords` 配置数组中配置。要了解更多关于编写自定义用户提供者的信息，请参阅 [身份验证文档](/docs/laravel/12.x/authentication#adding-custom-user-providers)。

<a name="deleting-expired-tokens"></a>
## 删除过期令牌

已过期的密码重置令牌仍将存在于您的数据库中。不过，您可以使用 `auth:clear-resets` Artisan 命令轻松删除这些记录：

```shell
php artisan auth:clear-resets
```

如果您想自动化此过程，请考虑将该命令添加到应用程序的 [调度器](/docs/laravel/12.x/scheduling) 中：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('auth:clear-resets')->everyFifteenMinutes();
```

<a name="password-customization"></a>
## 自定义

<a name="reset-link-customization"></a>
#### 重置链接自定义

您可以使用 `ResetPassword` 通知类提供的 `createUrlUsing` 方法自定义密码重置链接 URL。此方法接受一个闭包，该闭包接收正在接收通知的用户实例以及密码重置链接令牌。通常，您应该从 `App\Providers\AppServiceProvider` 服务提供者的 `boot` 方法中调用此方法：

```php
use App\Models\User;
use Illuminate\Auth\Notifications\ResetPassword;

/**
 * 引导任何应用程序服务。
 */
public function boot(): void
{
    ResetPassword::createUrlUsing(function (User $user, string $token) {
        return 'https://example.com/reset-password?token='.$token;
    });
}
```

<a name="reset-email-customization"></a>


#### 重置邮件自定义

你可以轻松修改用于向用户发送密码重置链接的通知类。 首先，覆盖你的 `App\Models\User` 模型上的 `sendPasswordResetNotification` 方法。 在此方法中，你可以使用你自己创建的任何 [消息通知类](/docs/laravel/12.x/notifications) 发送通知。 密码重置 `$token` 是该方法收到的第一个参数。 你可以使用这个 `$token` 来构建你选择的密码重置 URL 并将你的通知发送给用户：

```php
use App\Notifications\ResetPasswordNotification;

/**
 * 发送密码重置通知给用户.
 *
 * @param  string  $token
 */
public function sendPasswordResetNotification($token): void
{
    $url = 'https://example.com/reset-password?token='.$token;

    $this->notify(new ResetPasswordNotification($url));
}
```
