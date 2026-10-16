# 邮箱验证

- [简介](#introduction)
    - [模型准备](#model-preparation)
    - [数据库准备](#database-preparation)
- [路由](#verification-routing)
    - [邮箱验证提示](#the-email-verification-notice)
    - [邮箱验证处理器](#the-email-verification-handler)
    - [重新发送验证邮件](#resending-the-verification-email)
    - [保护路由](#protecting-routes)
- [自定义](#customization)
- [事件](#events)

<a name="introduction"></a>
## 简介

许多 Web 应用要求用户先验证邮箱地址，才能使用应用。Laravel 内置了便捷的服务，可发送邮箱验证邮件并校验验证请求，让你无需在每个新应用中手动实现这项功能。

> [!NOTE]
> 想要快速上手？在全新的 Laravel 应用中安装一个 [Laravel 应用入门套件](/docs/{{version}}/starter-kits)。入门套件会为你搭建完整的身份认证系统，包括邮箱验证功能。

<a name="model-preparation"></a>
### 模型准备

开始之前，请确认你的 `App\Models\User` 模型实现了 `Illuminate\Contracts\Auth\MustVerifyEmail` 接口：

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

模型实现这个接口后，新注册的用户就会自动收到一封包含邮箱验证链接的邮件。这个过程无需额外配置，因为 Laravel 会自动为 `Illuminate\Auth\Events\Registered` 事件注册 `Illuminate\Auth\Listeners\SendEmailVerificationNotification` [监听器](/docs/{{version}}/events)。

如果你在应用中手动实现注册功能，而没有使用[入门套件](/docs/{{version}}/starter-kits)，应确保在用户注册成功后派发 `Illuminate\Auth\Events\Registered` 事件：

```php
use Illuminate\Auth\Events\Registered;

event(new Registered($user));
```

<a name="database-preparation"></a>
### 数据库准备

接下来，你的 `users` 表必须包含 `email_verified_at` 列，用于存储用户邮箱地址验证通过的日期和时间。Laravel 默认的 `0001_01_01_000000_create_users_table.php` 数据库迁移通常已经包含这个列。

<a name="verification-routing"></a>
## 路由

要正确实现邮箱验证，需要定义三条路由。第一条路由用于向用户显示提示，告知他们应点击注册后由 Laravel 发送的验证邮件中的邮箱验证链接。

第二条路由用于处理用户点击邮件中的邮箱验证链接时发出的请求。

第三条路由用于在用户意外丢失首次验证链接时，重新发送验证链接。

<a name="the-email-verification-notice"></a>
### 邮箱验证提示

如前所述，应定义一条路由，返回一个视图，提示用户点击注册后由 Laravel 通过邮件发送给他们的邮箱验证链接。当用户尚未验证邮箱地址就尝试访问应用的其他部分时，应用会显示这个视图。请记住，只要你的 `App\Models\User` 模型实现了 `MustVerifyEmail` 接口，验证链接就会自动发送到用户的邮箱：

```php
Route::get('/email/verify', function () {
    return view('auth.verify-email');
})->middleware('auth')->name('verification.notice');
```

返回邮箱验证提示的路由应命名为 `verification.notice`。必须使用这个确切的名称，因为 [Laravel 自带的](#protecting-routes) `verified` 中间件会在用户尚未验证邮箱地址时，自动重定向到这个命名路由。

> [!NOTE]
> 手动实现邮箱验证时，你需要自行定义验证提示视图的内容。如果希望直接生成包含所有必要身份认证和验证视图的应用骨架，请参阅 [Laravel 应用入门套件](/docs/{{version}}/starter-kits)。

<a name="the-email-verification-handler"></a>
### 邮箱验证处理器

接下来，需要定义一条路由，处理用户点击邮件中的邮箱验证链接时发出的请求。这个路由应命名为 `verification.verify`，并附加 `auth` 和 `signed` 中间件：

```php
use Illuminate\Foundation\Auth\EmailVerificationRequest;

Route::get('/email/verify/{id}/{hash}', function (EmailVerificationRequest $request) {
    $request->fulfill();

    return redirect('/home');
})->middleware(['auth', 'signed'])->name('verification.verify');
```

继续之前，我们先仔细看看这个路由。首先，这里使用的是 `EmailVerificationRequest` 请求类型，而不是常见的 `Illuminate\Http\Request` 实例。`EmailVerificationRequest` 是 Laravel 自带的[表单请求](/docs/{{version}}/validation#form-request-validation)，会自动验证请求中的 `id` 和 `hash` 参数。

接下来，可以直接调用请求的 `fulfill` 方法。这个方法会调用已认证用户的 `markEmailAsVerified` 方法，并派发 `Illuminate\Auth\Events\Verified` 事件。默认的 `App\Models\User` 模型通过 `Illuminate\Foundation\Auth\User` 基类获得 `markEmailAsVerified` 方法。用户的邮箱地址验证通过后，你可以将其重定向到任意位置。

<a name="resending-the-verification-email"></a>
### 重新发送验证邮件

有时，用户可能会找不到或误删邮箱验证邮件。为此，你可以定义一条路由，允许用户请求重新发送验证邮件。然后，在[验证提示视图](#the-email-verification-notice)中放置一个简单的表单提交按钮，向这条路由发起请求：

```php
use Illuminate\Http\Request;

Route::post('/email/verification-notification', function (Request $request) {
    $request->user()->sendEmailVerificationNotification();

    return back()->with('message', 'Verification link sent!');
})->middleware(['auth', 'throttle:6,1'])->name('verification.send');
```

<a name="protecting-routes"></a>
### 保护路由

[路由中间件](/docs/{{version}}/middleware)可用于限制指定路由只允许已验证邮箱的用户访问。Laravel 提供了 `verified` [中间件别名](/docs/{{version}}/middleware#middleware-aliases)，它对应 `Illuminate\Auth\Middleware\EnsureEmailIsVerified` 中间件类。Laravel 已经自动注册了这个别名，因此你只需将 `verified` 中间件附加到路由定义上。通常，这个中间件会与 `auth` 中间件配合使用：

```php
Route::get('/profile', function () {
    // 只有已验证邮箱的用户才能访问此路由……
})->middleware(['auth', 'verified']);
```

如果尚未验证邮箱的用户尝试访问附加了这个中间件的路由，就会被自动重定向到 `verification.notice` [命名路由](/docs/{{version}}/routing#named-routes)。

<a name="customization"></a>
## 自定义

<a name="verification-email-customization"></a>
#### 自定义验证邮件

默认的邮箱验证通知可以满足大多数应用的需求，但 Laravel 也允许你自定义验证邮件的构建方式。

首先，将一个闭包传给 `Illuminate\Auth\Notifications\VerifyEmail` 通知提供的 `toMailUsing` 方法。这个闭包会接收两个参数：接收通知的模型实例，以及用户必须访问以验证邮箱地址的已签名验证 URL。闭包应返回一个 `Illuminate\Notifications\Messages\MailMessage` 实例。通常，应在应用的 `AppServiceProvider` 类的 `boot` 方法中调用 `toMailUsing` 方法：

```php
use Illuminate\Auth\Notifications\VerifyEmail;
use Illuminate\Notifications\Messages\MailMessage;

/**
 * 初始化应用服务。
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

> [!NOTE]
> 要了解更多邮件通知相关内容，请参阅[邮件通知文档](/docs/{{version}}/notifications#mail-notifications)。

<a name="events"></a>
## 事件

使用 [Laravel 应用入门套件](/docs/{{version}}/starter-kits)时，Laravel 会在邮箱验证过程中派发 `Illuminate\Auth\Events\Verified` [事件](/docs/{{version}}/events)。如果你在应用中手动处理邮箱验证，也可以在验证完成后手动派发这些事件。
