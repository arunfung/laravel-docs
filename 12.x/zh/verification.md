
# 邮箱验证

-   [简介](#introduction)
    -   [模型准备](#model-preparation)
    -   [数据库准备](#database-preparation)
-   [路由](#verification-routing)
    -   [邮箱验证通知](#the-email-verification-notice)
    -   [邮箱验证处理器](#the-email-verification-handler)
    -   [重新发送验证邮件](#resending-the-verification-email)
    -   [保护路由](#protecting-routes)
-   [自定义](#customization)
-   [事件](#events)

## 简介

许多 Web 应用在使用之前需要用户验证其电子邮箱地址。Laravel 提供了方便的内置服务来发送和验证邮箱验证请求，而不是强迫你在每个创建的应用中手动重新实现这个功能。

> [!注意]
> 想要快速开始？在一个全新的 Laravel 应用中安装 [Laravel 应用程序入门套件](/docs/laravel/12.x/starter-kits)。入门套件会处理整个认证系统的脚手架，包括邮箱验证支持。


### 模型准备

在开始之前，请确认你的 `App\Models\User` 模型实现了 `Illuminate\Contracts\Auth\MustVerifyEmail` 接口：

```php
<?php

namespace App\Models;

use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class User extends Authenticatable implements MustVerifyEmail
{
    use Notifiable;

    // ...
}
```

一旦这个接口被添加到模型中，新注册的用户将会自动收到一封包含邮箱验证链接的邮件。这是无缝发生的，因为 Laravel 会自动为 `Illuminate\Auth\Events\Registered` 事件注册 `Illuminate\Auth\Listeners\SendEmailVerificationNotification` [监听器](/docs/laravel/12.x/events)。

如果你是在应用中手动实现注册（而不是使用 [入门套件](/docs/laravel/12.x/starter-kits)），你需要确保在用户注册成功后派发 `Illuminate\Auth\Events\Registered` 事件：

```php
use Illuminate\Auth\Events\Registered;

event(new Registered($user));
```



### 数据库准备

接下来，你的 `users` 表必须包含一个 `email_verified_at` 列，用于存储用户邮箱地址被验证的日期和时间。通常，这个列会包含在 Laravel 默认的 `0001_01_01_000000_create_users_table.php` 数据库迁移文件中。

## 路由

要正确实现邮箱验证，需要定义三条路由。

第一条路由用于向用户显示提示，告知他们应点击注册后由 Laravel 发送的验证邮件中的邮箱验证链接。

第二条路由用于处理当用户点击验证邮件中的邮箱验证链接时产生的请求。

第三条路由用于在用户不小心丢失首次验证链接时，重新发送验证链接。

### 邮箱验证通知

如前所述，应定义一个路由，该路由会返回一个视图，指示用户点击注册后由 Laravel 通过邮件发送给他们的邮箱验证链接。当用户在未先验证邮箱地址的情况下尝试访问应用程序的其他部分时，将显示此视图。请记住，只要你的 `App\Models\User` 模型实现了 `MustVerifyEmail` 接口，验证链接就会自动发送到用户的邮箱：

```php
Route::get('/email/verify', function () {
    return view('auth.verify-email');
})->middleware('auth')->name('verification.notice');
```

返回邮箱验证通知的路由应命名为 `verification.notice`。为此路由分配这个确切的名称非常重要，因为 Laravel 自带的 `verified` 中间件（[保护路由](#protecting-routes)）会在用户尚未验证邮箱地址时自动重定向到该路由名称。

> [!注意]
> 当手动实现邮箱验证时，你需要自己定义邮箱验证通知视图的内容。
如果你想要包含所有必要认证和验证视图的脚手架，请查看 [Laravel 应用程序入门套件](/docs/laravel/12.x/starter-kits)。



### 邮箱验证处理器

接下来，我们需要定义一个路由，用来处理用户点击验证邮件中的邮箱验证链接时产生的请求。该路由应命名为 `verification.verify`，并分配 `auth` 和 `signed` 中间件：

```php
use Illuminate\Foundation\Auth\EmailVerificationRequest;

Route::get('/email/verify/{id}/{hash}', function (EmailVerificationRequest $request) {
    $request->fulfill();

    return redirect('/home');
})->middleware(['auth', 'signed'])->name('verification.verify');
```

在继续之前，我们先仔细看看这个路由。首先，你会注意到我们使用的是 `EmailVerificationRequest` 请求类型，而不是常见的 `Illuminate\Http\Request` 实例。`EmailVerificationRequest` 是 Laravel 自带的一个[表单请求](/docs/laravel/12.x/validation#form-request-validation)，它会自动负责验证请求中的 `id` 和 `hash` 参数。

接下来，我们可以直接调用请求对象的 `fulfill` 方法。该方法会调用已认证用户的 `markEmailAsVerified` 方法，并触发 `Illuminate\Auth\Events\Verified` 事件。`markEmailAsVerified` 方法可通过 `Illuminate\Foundation\Auth\User` 基类在默认的 `App\Models\User` 模型中使用。用户的邮箱地址验证成功后，你可以将他们重定向到任意你想要的位置。

### 重新发送验证邮件

有时，用户可能会丢失或误删邮箱验证邮件。为了应对这种情况，你可以定义一个路由，允许用户请求重新发送验证邮件。然后，你可以在[邮箱验证通知视图](#the-email-verification-notice)中放置一个简单的表单提交按钮，请求该路由：

```php
use Illuminate\Http\Request;

Route::post('/email/verification-notification', function (Request $request) {
    $request->user()->sendEmailVerificationNotification();

    return back()->with('message', 'Verification link sent!');
})->middleware(['auth', 'throttle:6,1'])->name('verification.send');
```



### 路由保护

[路由中间件](/docs/laravel/12.x/middleware) 可用于只允许已验证邮箱的用户访问指定路由。Laravel 自带一个 `verified` [中间件别名](/docs/laravel/12.x/middleware#middleware-aliases)，它是 `Illuminate\Auth\Middleware\EnsureEmailIsVerified` 中间件类的别名。由于这个别名已经被 Laravel 自动注册，所以你只需要将 `verified` 中间件附加到路由定义中即可。通常，这个中间件会和 `auth` 中间件一起使用：

```php
Route::get('/profile', function () {
     // 只有已验证邮箱的用户才能访问此路由...
})->middleware(['auth', 'verified']);
```

如果一个未验证邮箱的用户尝试访问分配了该中间件的路由，他们将会被自动重定向到 `verification.notice` [命名路由](/docs/laravel/12.x/routing#named-routes)。

## 自定义

#### 验证邮件自定义

尽管默认的邮箱验证通知可以满足大多数应用的需求，但 Laravel 允许你自定义验证邮件的构建方式。

首先，将一个闭包传递给 `Illuminate\Auth\Notifications\VerifyEmail` 通知提供的 `toMailUsing` 方法。该闭包会接收两个参数：接收通知的可通知（notifiable）模型实例，以及用户必须访问以验证邮箱地址的已签名邮箱验证 URL。闭包应返回一个 `Illuminate\Notifications\Messages\MailMessage` 实例。通常，你应该在应用的 `AppServiceProvider` 类的 `boot` 方法中调用 `toMailUsing` 方法

```php
use Illuminate\Auth\Notifications\VerifyEmail;
use Illuminate\Notifications\Messages\MailMessage;

/**
 * 启动任何应用服务。
 */
public function boot(): void
{
    // ...

    VerifyEmail::toMailUsing(function (object $notifiable, string $url) {
        return (new MailMessage)
            ->subject('Verify Email Address')
            ->line('Click the button below to verify your email address.')
            ->action('Verify Email Address', $url);
    });
}
```

> [!注意]
> 要了解更多关于邮件通知的内容，请参阅 [邮件通知文档](/docs/laravel/12.x/notifications#mail-notifications)。



<a name="events"></a>
## 事件

使用 Laravel [入门套件](/docs/laravel/12.x/starter-kits)时，Laravel 在电子邮件验证过程中会派发 `Illuminate\Auth\Events\Verified` [事件](/docs/laravel/12.x/events) 。如果你想让你的应用手动处理邮箱验证，你可以在验证完成后手动分发这些事件。
