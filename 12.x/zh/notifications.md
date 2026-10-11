
# 通知系统

- [简介](#introduction)
- [生成通知](#generating-notifications)
- [发送通知](#sending-notifications)
    - [使用Notifiable Trait](#using-the-notifiable-trait)
    - [使用Notification门面](#using-the-notification-facade)
    - [指定发送渠道](#specifying-delivery-channels)
    - [队列化通知](#queueing-notifications)
    - [即时需求通知](#on-demand-notifications)
- [邮件通知](#mail-notifications)
    - [格式化邮件消息](#formatting-mail-messages)
    - [自定义发件人](#customizing-the-sender)
    - [自定义收件人](#customizing-the-recipient)
    - [自定义邮件主题](#customizing-the-subject)
    - [自定义邮件发送器](#customizing-the-mailer)
    - [自定义邮件模板](#customizing-the-templates)
    - [邮件附件](#mail-attachments)
    - [添加标签和元数据](#adding-tags-metadata)
    - [自定义Symfony消息](#customizing-the-symfony-message)
    - [使用Mailable类](#using-mailables)
    - [预览邮件通知](#previewing-mail-notifications)
- [Markdown邮件通知](#markdown-mail-notifications)
    - [生成消息](#generating-the-message)
    - [编写消息内容](#writing-the-message)
    - [自定义组件](#customizing-the-components)
- [数据库通知](#database-notifications)
    - [前提条件](#database-prerequisites)
    - [格式化数据库通知](#formatting-database-notifications)
    - [访问通知](#accessing-the-notifications)
    - [标记通知为已读](#marking-notifications-as-read)
- [广播通知](#broadcast-notifications)
    - [前提条件](#broadcast-prerequisites)
    - [格式化广播通知](#formatting-broadcast-notifications)
    - [监听通知](#listening-for-notifications)
- [短信通知](#sms-notifications)
    - [前提条件](#sms-prerequisites)
    - [格式化短信通知](#formatting-sms-notifications)
    - [Unicode内容](#unicode-content)
    - [自定义发送号码](#customizing-the-from-number)
    - [添加客户端引用](#adding-a-client-reference)
    - [路由短信通知](#routing-sms-notifications)
- [Slack通知](#slack-notifications)
    - [前提条件](#slack-prerequisites)
    - [格式化Slack通知](#formatting-slack-notifications)
    - [Slack交互功能](#slack-interactivity)
    - [路由Slack通知](#routing-slack-notifications)
    - [通知外部Slack工作区](#notifying-external-slack-workspaces)
- [本地化通知](#localizing-notifications)
- [测试](#testing)
- [通知事件](#notification-events)
- [自定义渠道](#custom-channels)

<a name="introduction"></a>
## 简介

除了支持[邮件发送](/docs/laravel/12.x/mail), 功能外，Laravel 还提供了跨多种渠道发送通知的能力，包括邮件、短信（通过 [Vonage](https://www.vonage.com/communications-apis/)，原Nexmo服务）以及[Slack](https://slack.com)消息。此外，社区还开发了 [community built notification channels](https://laravel-notification-channels.com/about/#suggesting-a-new-channel) 大量通知渠道扩展，支持通过数十种不同渠道发送通知！这些通知还可以存储在数据库中，以便在您的Web界面中展示。



通常情况下，通知应该是简短的、信息性的消息，用于通知用户在你的应用程序中发生了某些事情。例如，如果你正在编写一个计费应用程序，你可能会通过电子邮件和短信渠道向用户发送一个“发票已支付”通知。

## 生成通知

在 Laravel 中，每个通知由一个单独的类表示，通常存储在 `app/Notifications` 目录中。如果你在应用程序中没有看到该目录，不用担心——当你运行 `make:notification` Artisan 命令时，它会自动为你创建：

```shell
php artisan make:notification InvoicePaid
```

该命令会在 `app/Notifications` 目录中放置一个新的通知类。每个通知类都包含一个 `via` 方法，以及若干消息构建方法（如 `toMail` 或 `toDatabase`），用于将通知转换为针对特定渠道的消息。

## 发送通知

### 使用 Notifiable 特征（Trait）

通知可以通过两种方式发送：使用 `Notifiable` 特征的 `notify` 方法，或者使用 `Notification` [门面（facade）](/docs/laravel/12.x/facades)。`Notifiable` 特征默认包含在你应用的 `App\Models\User` 模型中：

```php
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class User extends Authenticatable
{
    use Notifiable;
}
```

由该特征提供的 `notify` 方法需要接收一个通知实例：

```php
use App\Notifications\InvoicePaid;

$user->notify(new InvoicePaid($invoice));
```
> [!注意]
> 请记住，你可以在任何模型上使用 `Notifiable` 特征，并不仅限于 `User` 模型。



### 使用 Notification 门面（Facade）

或者，你也可以通过 `Notification` [门面](/docs/laravel/12.x/facades) 发送通知。当你需要向多个可通知实体（例如用户集合）发送通知时，这种方法非常有用。要使用门面发送通知，将所有可通知实体和通知实例传递给 `send` 方法：

```php
use Illuminate\Support\Facades\Notification;

Notification::send($users, new InvoicePaid($invoice));
```

你还可以使用 `sendNow` 方法立即发送通知。即使通知实现了 `ShouldQueue` 接口，该方法也会立即发送通知：

```php
Notification::sendNow($developers, new DeploymentCompleted($deployment));
```

### 指定发送渠道

每个通知类都有一个 `via` 方法，用于确定通知将通过哪些渠道发送。通知可以通过 `mail`、`database`、`broadcast`、`vonage` 和 `slack` 渠道发送。

> [!注意]
> 如果你想使用其他发送渠道，例如 Telegram 或 Pusher，可以查看社区维护的 [Laravel Notification Channels 网站](http://laravel-notification-channels.com)。

`via` 方法接收一个 `$notifiable` 实例，它将是通知发送目标的类的实例。你可以使用 `$notifiable` 来确定通知应该通过哪些渠道发送：

```php
/**
 * 获取通知的发送渠道。
 *
 * @return array<int, string>
 */
public function via(object $notifiable): array
{
    return $notifiable->prefers_sms ? ['vonage'] : ['mail', 'database'];
}
```

### 队列通知

> [!警告]
> 在将通知加入队列之前，你应该先配置队列并 [启动队列工作进程](/docs/laravel/12.x/queues#running-the-queue-worker)。



发送通知可能会耗费时间，尤其是当某个渠道需要调用外部 API 来发送通知时。为了加快应用程序的响应时间，可以通过在通知类中添加 `ShouldQueue` 接口和 `Queueable` 特征，让通知加入队列。使用 `make:notification` 命令生成的所有通知类中，这个接口和特征已经被导入，因此你可以立即将它们添加到你的通知类中：

```php
<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Notification;

class InvoicePaid extends Notification implements ShouldQueue
{
    use Queueable;

    // ...
}
```

一旦通知类实现了 `ShouldQueue` 接口，你可以像平常一样发送通知。Laravel 会检测类中是否实现了 `ShouldQueue` 接口，并自动将通知的发送加入队列：

```php
$user->notify(new InvoicePaid($invoice));
```

当通知加入队列时，每个接收者和每个渠道组合都会创建一个队列任务。例如，如果你的通知有三个接收者和两个渠道，将会有六个任务被派发到队列中。

#### 延迟发送通知

如果你想延迟通知的发送，可以在实例化通知时链式调用 `delay` 方法：

```php
$delay = now()->addMinutes(10);

$user->notify((new InvoicePaid($invoice))->delay($delay));
```

你也可以向 `delay` 方法传递一个数组，为特定渠道指定延迟时间：

```php
$user->notify((new InvoicePaid($invoice))->delay([
    'mail' => now()->addMinutes(5),
    'sms' => now()->addMinutes(10),
]));
```

或者，你可以在通知类本身定义一个 `withDelay` 方法。`withDelay` 方法应该返回一个渠道名称和延迟时间的数组：

```php
/**
 * 确定通知的发送延迟时间。
 *
 * @return array<string, \Illuminate\Support\Carbon>
 */
public function withDelay(object $notifiable): array
{
    return [
        'mail' => now()->addMinutes(5),
        'sms' => now()->addMinutes(10),
    ];
}
```



#### 自定义通知队列连接

默认情况下，加入队列的通知会使用应用程序的默认队列连接。如果你想为特定通知指定不同的连接，可以在通知构造函数中调用 `onConnection` 方法：

```php
<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Notification;

class InvoicePaid extends Notification implements ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的通知实例。
     */
    public function __construct()
    {
        $this->onConnection('redis');
    }
}
```

或者，如果你想为通知支持的每个渠道指定特定的队列连接，可以在通知类中定义 `viaConnections` 方法。该方法应返回一个渠道名称 / 队列连接名称的数组：

```php
/**
 * 确定每个通知渠道应使用的连接。
 *
 * @return array<string, string>
 */
public function viaConnections(): array
{
    return [
        'mail' => 'redis',
        'database' => 'sync',
    ];
}
```

#### 自定义通知渠道队列

如果你想为通知支持的每个渠道指定特定的队列，可以在通知类中定义 `viaQueues` 方法。该方法应返回一个渠道名称 / 队列名称的数组：

```php
/**
 * 确定每个通知渠道应使用的队列。
 *
 * @return array<string, string>
 */
public function viaQueues(): array
{
    return [
        'mail' => 'mail-queue',
        'slack' => 'slack-queue',
    ];
}
```

#### 队列通知中间件

加入队列的通知可以定义中间件，[就像队列任务一样](/docs/laravel/12.x/queues#job-middleware)。要开始使用，可以在通知类中定义一个 `middleware` 方法。该方法会接收 `$notifiable` 和 `$channel` 变量，允许你根据通知的目标自定义返回的中间件：

```php
use Illuminate\Queue\Middleware\RateLimited;

/**
 * 获取通知队列任务应通过的中间件。
 *
 * @return array<int, object>
 */
public function middleware(object $notifiable, string $channel)
{
    return match ($channel) {
        'mail' => [new RateLimited('postmark')],
        'slack' => [new RateLimited('slack')],
        default => [],
    };
}
```



#### 队列通知与数据库事务

当在数据库事务中派发队列通知时，这些通知可能在数据库事务提交之前就被队列处理。这种情况下，你在数据库事务中对模型或数据库记录所做的任何更新可能尚未反映在数据库中。此外，在事务中创建的任何模型或数据库记录可能尚不存在于数据库中。如果你的通知依赖这些模型，当处理发送队列通知的任务时，可能会发生意外错误。

如果你的队列连接的 `after_commit` 配置选项被设置为 `false`，你仍然可以通过在发送通知时调用 `afterCommit` 方法来指示某个队列通知应在所有未提交的数据库事务完成后再派发：

```php
use App\Notifications\InvoicePaid;

$user->notify((new InvoicePaid($invoice))->afterCommit());
```

或者，你也可以在通知类的构造函数中调用 `afterCommit` 方法：

```php
<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Notification;

class InvoicePaid extends Notification implements ShouldQueue
{
    use Queueable;

    /**
     * 创建一个新的通知实例。
     */
    public function __construct()
    {
        $this->afterCommit();
    }
}
```

> [!注意]
> 想要了解如何解决这些问题，请查看关于 [队列任务与数据库事务](/docs/laravel/12.x/queues#jobs-and-database-transactions) 的文档。

#### 判断队列通知是否应该发送

当队列通知已派发到队列以进行后台处理后，它通常会被队列工作进程接受，并发送给其预期的接收者。



然而，如果你希望在队列工作进程处理通知后，最终决定是否发送队列通知，可以在通知类中定义一个 `shouldSend` 方法。如果该方法返回 `false`，通知将不会被发送：

```php
/**
 * 判断该通知是否应该发送。
 */
public function shouldSend(object $notifiable, string $channel): bool
{
    return $this->invoice->isPaid();
}
```

### 按需发送通知

有时你可能需要向未存储为应用程序“用户”的人发送通知。使用 `Notification` 门面的 `route` 方法，你可以在发送通知之前指定临时的通知路由信息：

```php
use Illuminate\Broadcasting\Channel;
use Illuminate\Support\Facades\Notification;

Notification::route('mail', 'taylor@example.com')
    ->route('vonage', '5555555555')
    ->route('slack', '#slack-channel')
    ->route('broadcast', [new Channel('channel-name')])
    ->notify(new InvoicePaid($invoice));
```

如果你希望在向 `mail` 路由发送按需通知时提供收件人的姓名，可以传递一个数组，其中数组的键是电子邮件地址，值是姓名：

```php
Notification::route('mail', [
    'barrett@example.com' => 'Barrett Blair',
])->notify(new InvoicePaid($invoice));
```

使用 `routes` 方法，你可以一次性为多个通知渠道提供临时路由信息：

```php
Notification::routes([
    'mail' => ['barrett@example.com' => 'Barrett Blair'],
    'vonage' => '5555555555',
])->notify(new InvoicePaid($invoice));
```

## 邮件通知

### 邮件消息格式化



如果一个通知支持以电子邮件方式发送，你应该在通知类中定义一个 `toMail` 方法。该方法将接收一个 `$notifiable` 实体，并应返回一个 `Illuminate\Notifications\Messages\MailMessage` 实例。

`MailMessage` 类提供了一些简单的方法，帮助你构建事务性邮件消息。邮件消息可以包含文本行以及一个“行动按钮”。下面是一个示例 `toMail` 方法：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    $url = url('/invoice/'.$this->invoice->id);

    return (new MailMessage)
        ->greeting('Hello!')
        ->line('One of your invoices has been paid!')
        ->lineIf($this->amount > 0, "Amount paid: {$this->amount}")
        ->action('View Invoice', $url)
        ->line('Thank you for using our application!');
}
```

> [!注意]
> 请注意，我们在 `toMail` 方法中使用了 `$this->invoice->id`。你可以将通知生成消息所需的任何数据通过通知的构造函数传入。

在这个示例中，我们注册了问候语、一行文本、一条行动按钮，再加上一行文本。`MailMessage` 对象提供的方法使得格式化小型事务性邮件变得简单快捷。邮件渠道会将这些消息组件转换为漂亮且响应式的 HTML 邮件模板，并附带纯文本版本。下面是 `mail` 渠道生成的邮件示例：

<img src="https://laravel.com/img/docs/notification-example-2.png">

> [!注意]
> 发送邮件通知时，请确保在 `config/app.php` 配置文件中设置了 `name` 配置选项。该值会用于邮件通知消息的头部和底部。



#### 错误消息

有些通知用于向用户告知错误，例如发票支付失败。你可以在构建邮件消息时调用 `error` 方法，表明邮件是关于错误的。当在邮件消息上使用 `error` 方法时，行动按钮将变为红色而非黑色：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->error()
        ->subject('Invoice Payment Failed')
        ->line('...');
}
```

#### 其他邮件通知格式化选项

你可以不用在通知类中定义文本“行”，而是使用 `view` 方法指定一个自定义模板来渲染通知邮件：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)->view(
        'mail.invoice.paid', ['invoice' => $this->invoice]
    );
}
```

你可以通过将纯文本视图名称作为数组的第二个元素传递给 `view` 方法，为邮件消息指定纯文本视图：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)->view(
        ['mail.invoice.paid', 'mail.invoice.paid-text'], // HTML 视图 + 纯文本视图
        ['invoice' => $this->invoice]
    );
}
```

或者，如果你的消息只有纯文本视图，可以使用 `text` 方法：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)->text(
        'mail.invoice.paid-text', ['invoice' => $this->invoice] // 仅纯文本邮件
    );
}
```



### 自定义发件人

默认情况下，邮件的发件人 / from 地址是在 `config/mail.php` 配置文件中定义的。
但是，你可以通过 `from` 方法为某个特定通知指定发件人地址：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->from('barrett@example.com', 'Barrett Blair')
        ->line('...');
}
```

### 自定义收件人

当通过 `mail` 渠道发送通知时，通知系统会自动查找可通知实体上的 `email` 属性。
你可以通过在可通知实体上定义一个 `routeNotificationForMail` 方法，来自定义用于发送通知的邮箱地址：

```php
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Illuminate\Notifications\Notification;

class User extends Authenticatable
{
    use Notifiable;

    /**
     * 为 mail 渠道路由通知。
     *
     * @return  array<string, string>|string
     */
    public function routeNotificationForMail(Notification $notification): array|string
    {
        // 仅返回邮箱地址...
        return $this->email_address;

        // 返回邮箱地址和姓名...
        return [$this->email_address => $this->name];
    }
}
```

### 自定义主题

默认情况下，邮件的主题是通知类名转换成 “标题格式（Title Case）” 后的结果。
所以，如果你的通知类名是 `InvoicePaid`，邮件的主题就是 `Invoice Paid`。
如果你想为消息指定不同的主题，可以在构建消息时调用 `subject` 方法：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->subject('Notification Subject')
        ->line('...');
}
```



### 自定义 Mailer

默认情况下，邮件通知会使用 `config/mail.php` 配置文件中定义的默认 mailer 发送。
但是，你可以在运行时通过在构建消息时调用 `mailer` 方法来指定一个不同的 mailer：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->mailer('postmark')
        ->line('...');
}
```

### 自定义模板

你可以通过发布通知包的资源，修改邮件通知所使用的 HTML 和纯文本模板。
运行以下命令后，邮件通知模板将会被放置在 `resources/views/vendor/notifications` 目录下：

```shell
php artisan vendor:publish --tag=laravel-notifications
```

### 附件

要在邮件通知中添加附件，可以在构建消息时使用 `attach` 方法。
`attach` 方法的第一个参数接受文件的绝对路径：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->greeting('Hello!')
        ->attach('/path/to/file');
}
```

> [!注意]
> 通知邮件消息提供的 `attach` 方法同样支持 [attachable 对象](/docs/laravel/12.x/mail#attachable-objects)。
请查阅完整的 [attachable 对象文档](/docs/laravel/12.x/mail#attachable-objects) 了解更多信息。

当向消息附加文件时，你还可以通过将一个 `array` 作为第二个参数传递给 `attach` 方法，来指定显示名称和/或 MIME 类型：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->greeting('Hello!')
        ->attach('/path/to/file', [
            'as' => 'name.pdf',
            'mime' => 'application/pdf',
        ]);
}
```



与在 mailable 对象中附加文件不同，你不能直接使用 `attachFromStorage` 从存储磁盘附加文件。
你应该改为使用 `attach` 方法，并提供存储磁盘上文件的绝对路径。
或者，你也可以在 `toMail` 方法中返回一个 [mailable](/docs/laravel/12.x/mail#generating-mailables)：

```php
use App\Mail\InvoicePaid as InvoicePaidMailable;

/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): Mailable
{
    return (new InvoicePaidMailable($this->invoice))
        ->to($notifiable->email)
        ->attachFromStorage('/path/to/file');
}
```

在需要时，可以使用 `attachMany` 方法向消息附加多个文件：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->greeting('Hello!')
        ->attachMany([
            '/path/to/forge.svg',
            '/path/to/vapor.svg' => [
                'as' => 'Logo.svg',
                'mime' => 'image/svg+xml',
            ],
        ]);
}
```

#### 原始数据附件

`attachData` 方法可以用来将原始字节字符串作为附件附加。
调用 `attachData` 方法时，你应该提供一个文件名，用来分配给该附件：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->greeting('Hello!')
        ->attachData($this->pdf, 'name.pdf', [
            'mime' => 'application/pdf',
        ]);
}
```

### 添加标签和元数据

一些第三方邮件服务提供商（例如 Mailgun 和 Postmark）支持消息的 “标签（tags）” 和 “元数据（metadata）”，它们可用于对应用程序发送的电子邮件进行分组和追踪。
你可以通过 `tag` 和 `metadata` 方法将标签和元数据添加到电子邮件消息中：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->greeting('Comment Upvoted!')
        ->tag('upvote')
        ->metadata('comment_id', $this->comment->id);
}
```



如果你的应用正在使用 **Mailgun 驱动**，你可以查阅 Mailgun 的文档以获取更多关于 [标签（tags）](https://documentation.mailgun.com/en/latest/user_manual.html#tagging-1) 和 [元数据（metadata）](https://documentation.mailgun.com/en/latest/user_manual.html#attaching-data-to-messages) 的信息。
同样地，你也可以查阅 Postmark 的文档，以获取更多关于其对 [标签](https://postmarkapp.com/blog/tags-support-for-smtp) 和 [元数据](https://postmarkapp.com/support/article/1125-custom-metadata-faq) 的支持信息。

如果你的应用使用 **Amazon SES** 发送电子邮件，你应该使用 `metadata` 方法，将 [SES “标签”](https://docs.aws.amazon.com/ses/latest/APIReference/API_MessageTag.html) 附加到消息中。

### 自定义 Symfony Message

`MailMessage` 类的 `withSymfonyMessage` 方法允许你注册一个闭包（closure），在发送消息之前，该闭包会接收 Symfony Message 实例。
这为你提供了一个在消息被投递前进行深度自定义的机会：

```php
use Symfony\Component\Mime\Email;

/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->withSymfonyMessage(function (Email $message) {
            $message->getHeaders()->addTextHeader(
                'Custom-Header', 'Header Value'
            );
        });
}
```

### 使用 Mailables

如果需要，你可以从通知的 `toMail` 方法返回一个完整的 [mailable 对象](/docs/laravel/12.x/mail)。
当返回的是 `Mailable` 而不是 `MailMessage` 时，你需要使用 mailable 对象的 `to` 方法来指定消息的收件人：

```php
use App\Mail\InvoicePaid as InvoicePaidMailable;
use Illuminate\Mail\Mailable;

/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): Mailable
{
    return (new InvoicePaidMailable($this->invoice))
        ->to($notifiable->email);
}
```



#### Mailables 与按需通知

如果你正在发送一个 [按需通知](#on-demand-notifications)，传递给 `toMail` 方法的 `$notifiable` 实例将会是 `Illuminate\Notifications\AnonymousNotifiable` 的一个实例。
该类提供了一个 `routeNotificationFor` 方法，可用于获取按需通知应发送到的邮箱地址：

```php
use App\Mail\InvoicePaid as InvoicePaidMailable;
use Illuminate\Notifications\AnonymousNotifiable;
use Illuminate\Mail\Mailable;

/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): Mailable
{
    $address = $notifiable instanceof AnonymousNotifiable
        ? $notifiable->routeNotificationFor('mail')
        : $notifiable->email;

    return (new InvoicePaidMailable($this->invoice))
        ->to($address);
}
```

### 预览邮件通知

在设计邮件通知模板时，能够像普通 Blade 模板一样在浏览器中快速预览渲染后的邮件消息是非常方便的。
为此，Laravel 允许你直接从路由闭包或控制器返回由邮件通知生成的任意邮件消息。
当返回的是一个 `MailMessage` 时，它会被渲染并显示在浏览器中，从而让你可以快速预览其设计，而无需实际将其发送到一个邮箱地址：

```php
use App\Models\Invoice;
use App\Notifications\InvoicePaid;

Route::get('/notification', function () {
    $invoice = Invoice::find(1);

    return (new InvoicePaid($invoice))
        ->toMail($invoice->user);
});
```

## Markdown 邮件通知

Markdown 邮件通知允许你在利用邮件通知的预构建模板的同时，获得更大的自由度来编写更长、更个性化的消息。
由于这些消息是用 Markdown 编写的，Laravel 能够将其渲染为美观、响应式的 HTML 模板，同时还能自动生成一个纯文本版本。



### 生成消息

要生成带有对应 Markdown 模板的通知，你可以在 `make:notification` Artisan 命令中使用 `--markdown` 选项：

```shell
php artisan make:notification InvoicePaid --markdown=mail.invoice.paid
```

和所有其他邮件通知一样，使用 Markdown 模板的通知也应该在其通知类中定义一个 `toMail` 方法。
不过，与其使用 `line` 和 `action` 方法来构建通知，不如使用 `markdown` 方法来指定应使用的 Markdown 模板名称。
你希望提供给模板使用的数据数组可以作为该方法的第二个参数传递：

```php
/**
 * 获取通知的邮件表示。
 */
public function toMail(object $notifiable): MailMessage
{
    $url = url('/invoice/'.$this->invoice->id);

    return (new MailMessage)
        ->subject('Invoice Paid')
        ->markdown('mail.invoice.paid', ['url' => $url]);
}
```

### 编写消息

Markdown 邮件通知结合了 Blade 组件和 Markdown 语法，
这样你可以轻松地构建通知，同时利用 Laravel 预先制作好的通知组件：

```blade
<x-mail::message>
# Invoice Paid

Your invoice has been paid!

<x-mail::button :url="$url">
View Invoice
</x-mail::button>

Thanks,<br>
{{ config('app.name') }}
</x-mail::message>
```

> [!注意]
> 在编写 Markdown 邮件时，不要使用过多缩进。根据 Markdown 标准，Markdown 解析器会将缩进内容渲染为代码块。

#### 按钮组件

按钮组件会渲染一个居中的按钮链接。
该组件接受两个参数：一个 `url`，以及一个可选的 `color`。
支持的颜色有：`primary`、`green` 和 `red`。
你可以在通知中添加任意数量的按钮组件：

```blade
<x-mail::button :url="$url" color="green">
View Invoice
</x-mail::button>
```



#### 面板组件

面板组件用于在通知中将给定的文本块渲染在一个面板中，该面板的背景颜色与通知的其他部分略有不同。这可以用来突出显示特定的文本块：

```blade
<x-mail::panel>
This is the panel content.
</x-mail::panel>
```

#### 表格组件

表格组件允许你将 Markdown 表格转换为 HTML 表格。该组件接受 Markdown 表格作为内容。表格列的对齐方式支持使用默认的 Markdown 表格对齐语法：

```blade
<x-mail::table>
| Laravel       | Table         | Example       |
| ------------- | :-----------: | ------------: |
| Col 2 is      | Centered      | $10           |
| Col 3 is      | Right-Aligned | $20           |
</x-mail::table>
```

### 自定义组件

你可以将所有 Markdown 通知组件导出到你的应用中进行自定义。要导出组件，可以使用 Artisan 命令 `vendor:publish` 来发布 `laravel-mail` 资源标签：

```shell
php artisan vendor:publish --tag=laravel-mail
```

此命令会将 Markdown 邮件组件发布到 `resources/views/vendor/mail` 目录下。`mail` 目录中将包含 `html` 和 `text` 两个子目录，每个子目录中包含所有可用组件的对应表示。你可以根据需要自定义这些组件。

#### 自定义 CSS

导出组件后，`resources/views/vendor/mail/html/themes` 目录中将包含一个 `default.css` 文件。你可以在此文件中自定义 CSS，你的样式将自动内联到 Markdown 通知的 HTML 表示中。

如果你希望为 Laravel 的 Markdown 组件构建一个全新的主题，可以将 CSS 文件放置在 `html/themes` 目录下。命名并保存文件后，在 `mail` 配置文件中将 `theme` 选项更新为你的新主题名称即可。




要为单个通知自定义主题，你可以在构建通知的邮件消息时调用 `theme` 方法。`theme` 方法接受发送通知时应使用的主题名称：

```php
/**
 * 获取通知的邮件表示
 */
public function toMail(object $notifiable): MailMessage
{
    return (new MailMessage)
        ->theme('invoice')
        ->subject('Invoice Paid')
        ->markdown('mail.invoice.paid', ['url' => $url]);
}
```

## 数据库通知

### 前置条件

`database` 通知通道会将通知信息存储在数据库表中。该表将包含通知类型等信息，以及描述通知的 JSON 数据结构。

你可以查询该表，以在应用程序的用户界面中显示通知。但在此之前，你需要创建一个数据库表来存储通知。可以使用 `make:notifications-table` 命令生成一个带有正确表结构的 [迁移](/docs/laravel/12.x/migrations)：

```shell
php artisan make:notifications-table

php artisan migrate
```

> [!注意]
> 如果你的可通知模型（notifiable models）使用 [UUID 或 ULID 主键](/docs/laravel/12.x/eloquent#uuid-and-ulid-keys)，则应在通知表迁移中将 `morphs` 方法替换为 [uuidMorphs](/docs/laravel/12.x/migrations#column-method-uuidMorphs) 或 [ulidMorphs](/docs/laravel/12.x/migrations#column-method-ulidMorphs)。

### 格式化数据库通知（Formatting Database Notifications）

如果通知支持存储在数据库表中，你应该在通知类中定义 `toDatabase` 或 `toArray` 方法。该方法会接收一个 `$notifiable` 实体，并应返回一个普通的 PHP 数组。返回的数组会被编码为 JSON，并存储在 `notifications` 表的 `data` 列中。

下面是一个 `toArray` 方法的示例：

```php
/**
 * 获取通知的数组表示
 *
 * @return array<string, mixed>
 */
public function toArray(object $notifiable): array
{
    return [
        'invoice_id' => $this->invoice->id,
        'amount' => $this->invoice->amount,
    ];
}
```



当通知存储在应用程序的数据库中时，`type` 列默认会设置为通知的类名，而 `read_at` 列默认为 `null`。不过，你可以通过在通知类中定义 `databaseType` 和 `initialDatabaseReadAtValue` 方法来自定义此行为：

```php
use Illuminate\Support\Carbon;

/**
 * 获取通知的数据库类型
 */
public function databaseType(object $notifiable): string
{
    return 'invoice-paid';
}

/**
 * 获取 "read_at" 列的初始值
 */
public function initialDatabaseReadAtValue(): ?Carbon
{
    return null;
}
```

#### toDatabase 与 toArray 的区别

`toArray` 方法同样被 `broadcast` 通道使用，以确定要广播到 JavaScript 前端的数据。如果你希望 `database` 通道和 `broadcast` 通道使用不同的数组表示，应在通知类中定义 `toDatabase` 方法，而不是仅使用 `toArray` 方法。

### 访问通知（Accessing the Notifications）

一旦通知存储在数据库中，你需要一种方便的方式从可通知实体中访问它们。Laravel 默认 `App\Models\User` 模型中包含的 `Illuminate\Notifications\Notifiable` trait 提供了一个 `notifications` [Eloquent 关系](/docs/laravel/12.x/eloquent-relationships)，可以返回该实体的所有通知。要获取通知，你可以像访问其他 Eloquent 关系一样使用该方法。默认情况下，通知会按照 `created_at` 时间戳排序，最近的通知会出现在集合的开头：

```php
$user = App\Models\User::find(1);

foreach ($user->notifications as $notification) {
    echo $notification->type;
}
```

如果你只想获取“未读”通知，可以使用 `unreadNotifications` 关系。同样，这些通知会按 `created_at` 时间戳排序，最近的通知在集合开头：

```php
$user = App\Models\User::find(1);

foreach ($user->unreadNotifications as $notification) {
    echo $notification->type;
}
```

> [!注意]
> 若要从 JavaScript 客户端访问通知，你应为应用程序定义一个通知控制器，该控制器返回可通知实体（如当前用户）的通知。然后，你可以从 JavaScript 客户端向该控制器的 URL 发起 HTTP 请求。




### 标记通知为已读

通常，当用户查看通知时，你会希望将该通知标记为“已读”。`Illuminate\Notifications\Notifiable` trait 提供了 `markAsRead` 方法，它会更新通知数据库记录中的 `read_at` 列：

```php
$user = App\Models\User::find(1);

foreach ($user->unreadNotifications as $notification) {
    $notification->markAsRead();
}
```

不过，你也可以直接对通知集合使用 `markAsRead` 方法，而不需要循环每个通知：

```php
$user->unreadNotifications->markAsRead();
```

你还可以使用批量更新查询，将所有通知标记为已读，而无需先从数据库中获取它们：

```php
$user = App\Models\User::find(1);

$user->unreadNotifications()->update(['read_at' => now()]);
```

你也可以通过 `delete` 删除通知，将其从表中完全移除：

```php
$user->notifications()->delete();
```

## 广播通知

### 前置条件

在广播通知之前，你应该配置并熟悉 Laravel 的 [事件广播](/docs/laravel/12.x/broadcasting) 服务。事件广播提供了一种方式，让基于 JavaScript 的前端能够响应服务器端的 Laravel 事件。

### 格式化广播通知

`broadcast` 通道使用 Laravel 的 [事件广播](/docs/laravel/12.x/broadcasting) 服务广播通知，使你的 JavaScript 前端能够实时接收通知。如果通知支持广播，你可以在通知类中定义 `toBroadcast` 方法。该方法会接收一个 `$notifiable` 实体，并应返回一个 `BroadcastMessage` 实例。如果 `toBroadcast` 方法不存在，则会使用 `toArray` 方法来获取需要广播的数据。返回的数据会被编码为 JSON 并广播到前端。

下面是一个 `toBroadcast` 方法的示例：

```php
use Illuminate\Notifications\Messages\BroadcastMessage;

/**
 * 获取可广播的通知表示
 */
public function toBroadcast(object $notifiable): BroadcastMessage
{
    return new BroadcastMessage([
        'invoice_id' => $this->invoice->id,
        'amount' => $this->invoice->amount,
    ]);
}
```



#### 广播队列配置

所有广播通知都会进入队列进行广播。如果你想配置用于广播操作的队列连接或队列名称，可以使用 `BroadcastMessage` 的 `onConnection` 和 `onQueue` 方法：

```php
return (new BroadcastMessage($data))
    ->onConnection('sqs')
    ->onQueue('broadcasts');
```

#### 自定义通知类型

除了你指定的数据，所有广播通知还包含一个 `type` 字段，记录通知的完整类名。如果你希望自定义通知 `type`，可以在通知类中定义 `broadcastType` 方法：

```php
/**
 * 获取广播通知的类型
 */
public function broadcastType(): string
{
    return 'broadcast.message';
}
```

### 监听通知

通知将会在使用 `{notifiable}.{id}` 约定格式的私有通道上广播。例如，如果你发送通知给一个 ID 为 `1` 的 `App\Models\User` 实例，则通知会在 `App.Models.User.1` 私有通道上广播。使用 [Laravel Echo](/docs/laravel/12.x/broadcasting#client-side-installation) 时，你可以通过 `notification` 方法轻松监听通道上的通知：

```js
Echo.private('App.Models.User.' + userId)
    .notification((notification) => {
        console.log(notification.type);
    });
```

#### 自定义通知通道

如果你希望自定义实体广播通知的通道，可以在可通知实体上定义 `receivesBroadcastNotificationsOn` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Broadcasting\PrivateChannel;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class User extends Authenticatable
{
    use Notifiable;

    /**
     * 用户接收通知广播的通道
     */
    public function receivesBroadcastNotificationsOn(): string
    {
        return 'users.'.$this->id;
    }
}
```



## 短信通知

### 前置条件

在 Laravel 中发送短信通知由 [Vonage](https://www.vonage.com/)（原 Nexmo）提供支持。在通过 Vonage 发送通知之前，你需要安装以下包：

```shell
composer require laravel/vonage-notification-channel guzzlehttp/guzzle
```

该包包含一个 [配置文件](https://github.com/laravel/vonage-notification-channel/blob/3.x/config/vonage.php)，但你不必将此配置文件导出到自己的应用中。你可以直接使用环境变量 `VONAGE_KEY` 和 `VONAGE_SECRET` 来定义 Vonage 的公钥和私钥。

在定义密钥后，你还应设置 `VONAGE_SMS_FROM` 环境变量，用于定义默认发送短信的手机号。你可以在 Vonage 控制面板中生成此手机号：

```ini
VONAGE_SMS_FROM=15556666666
```

### 格式化短信通知

如果通知支持以短信方式发送，你应在通知类中定义 `toVonage` 方法。该方法会接收一个 `$notifiable` 实体，并应返回一个 `Illuminate\Notifications\Messages\VonageMessage` 实例：

```php
use Illuminate\Notifications\Messages\VonageMessage;

/**
 * 获取通知的 Vonage / 短信表示
 */
public function toVonage(object $notifiable): VonageMessage
{
    return (new VonageMessage)
        ->content('Your SMS message content');
}
```

#### Unicode 内容

如果短信内容包含 Unicode 字符，你应在构建 `VonageMessage` 实例时调用 `unicode` 方法：

```php
use Illuminate\Notifications\Messages\VonageMessage;

/**
 * 获取通知的 Vonage / 短信表示（Unicode）
 */
public function toVonage(object $notifiable): VonageMessage
{
    return (new VonageMessage)
        ->content('Your unicode message')
        ->unicode();
}
```



### 自定义“发件人”号码

如果你希望某些通知使用与 `VONAGE_SMS_FROM` 环境变量中指定的号码不同的电话号码发送，可以在 `VonageMessage` 实例上调用 `from` 方法：

```php
use Illuminate\Notifications\Messages\VonageMessage;

/**
 * 获取通知的 Vonage / 短信表示
 */
public function toVonage(object $notifiable): VonageMessage
{
    return (new VonageMessage)
        ->content('Your SMS message content')
        ->from('15554443333');
}
```

### 添加客户端参考

如果你希望按用户、团队或客户跟踪成本，可以为通知添加“客户端参考”（client reference）。Vonage 允许你使用此客户端参考生成报告，以便更好地了解特定客户的短信使用情况。客户端参考可以是任意长度不超过 40 个字符的字符串：

```php
use Illuminate\Notifications\Messages\VonageMessage;

/**
 * 获取通知的 Vonage / 短信表示
 */
public function toVonage(object $notifiable): VonageMessage
{
    return (new VonageMessage)
        ->clientReference((string) $notifiable->id)
        ->content('Your SMS message content');
}
```

### 路由短信通知

为了将 Vonage 通知发送到正确的电话号码，需要在可通知实体上定义 `routeNotificationForVonage` 方法：

```php
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Illuminate\Notifications\Notification;

class User extends Authenticatable
{
    use Notifiable;

    /**
     * 为 Vonage 渠道路由通知
     */
    public function routeNotificationForVonage(Notification $notification): string
    {
        return $this->phone_number;
    }
}
```

## Slack 通知



### 前置条件

在发送 Slack 通知之前，你需要通过 Composer 安装 Slack 通知通道：

```shell
composer require laravel/slack-notification-channel
```

此外，你必须为你的 Slack 工作区创建一个 [Slack App](https://api.slack.com/apps?new_app=1)。

如果你只需要向创建 App 的同一个 Slack 工作区发送通知，请确保你的 App 拥有以下权限（Scopes）：`chat:write`、`chat:write.public` 和 `chat:write.customize`。这些权限可以在 Slack 的 App 管理页面的 “OAuth & Permissions” 标签下添加。

接下来，将 App 的 **Bot User OAuth Token** 复制到你应用的 `services.php` 配置文件中的 `slack` 配置数组中。该 Token 可以在 Slack 的 “OAuth & Permissions” 标签页中找到：

```php
'slack' => [
    'notifications' => [
        'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
        'channel' => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
    ],
],
```

#### App 分发

如果你的应用需要向外部 Slack 工作区（由你的应用用户拥有）发送通知，你需要通过 Slack 分发你的 App。App 分发可以在 Slack 的 “Manage Distribution” 标签下管理。一旦 App 已分发，你可以使用 [Socialite](/docs/laravel/12.x/socialite) 代表你的应用用户获取 Slack Bot Token。

### 格式化 Slack 通知

如果通知支持通过 Slack 发送消息，你需要在通知类中定义 `toSlack` 方法。该方法会接收一个 `$notifiable` 实体，并应返回 `Illuminate\Notifications\Slack\SlackMessage` 实例。你可以使用 [Slack 的 Block Kit API](https://api.slack.com/block-kit) 构建丰富的通知。以下示例可在 [Slack 的 Block Kit builder](https://app.slack.com/block-kit-builder/T01KWS6K23Z#%7B%22blocks%22:%5B%7B%22type%22:%22header%22,%22text%22:%7B%22type%22:%22plain_text%22,%22text%22:%22Invoice%20Paid%22%7D%7D,%7B%22type%22:%22context%22,%22elements%22:%5B%7B%22type%22:%22plain_text%22,%22text%22:%22Customer%20%231234%22%7D%5D%7D,%7B%22type%22:%22section%22,%22text%22:%7B%22type%22:%22plain_text%22,%22text%22:%22An%20invoice%20has%20been%20paid.%22%7D,%22fields%22:%5B%7B%22type%22:%22mrkdwn%22,%22text%22:%22*Invoice%20No:*%5Cn1000%22%7D,%7B%22type%22:%22mrkdwn%22,%22text%22:%22*Invoice%20Recipient:*%5Cntaylor@laravel.com%22%7D%5D%7D,%7B%22type%22:%22divider%22%7D,%7B%22type%22:%22section%22,%22text%22:%7B%22type%22:%22plain_text%22,%22text%22:%22Congratulations!%22%7D%7D%5D%7D) 中预览：

```php
use Illuminate\Notifications\Slack\BlockKit\Blocks\ContextBlock;
use Illuminate\Notifications\Slack\BlockKit\Blocks\SectionBlock;
use Illuminate\Notifications\Slack\BlockKit\Composites\ConfirmObject;
use Illuminate\Notifications\Slack\SlackMessage;

/**
 * 获取通知的 Slack 表示
 */
public function toSlack(object $notifiable): SlackMessage
{
    return (new SlackMessage)
        ->text('One of your invoices has been paid!')
        ->headerBlock('Invoice Paid')
        ->contextBlock(function (ContextBlock $block) {
            $block->text('Customer #1234');
        })
        ->sectionBlock(function (SectionBlock $block) {
            $block->text('An invoice has been paid.');
            $block->field("*Invoice No:*\n1000")->markdown();
            $block->field("*Invoice Recipient:*\ntaylor@laravel.com")->markdown();
        })
        ->dividerBlock()
        ->sectionBlock(function (SectionBlock $block) {
            $block->text('Congratulations!');
        });
}
```



#### 使用 Slack 的 Block Kit Builder 模板

你可以不用流式方法来构建 Block Kit 消息，而是直接提供 Slack 的 Block Kit Builder 生成的原始 JSON 负载，传给 `usingBlockKitTemplate` 方法：

```php
use Illuminate\Notifications\Slack\SlackMessage;
use Illuminate\Support\Str;

/**
 * 获取通知的 Slack 表示
 */
public function toSlack(object $notifiable): SlackMessage
{
    $template = <<<JSON
        {
          "blocks": [
            {
              "type": "header",
              "text": {
                "type": "plain_text",
                "text": "Team Announcement"
              }
            },
            {
              "type": "section",
              "text": {
                "type": "plain_text",
                "text": "We are hiring!"
              }
            }
          ]
        }
    JSON;

    return (new SlackMessage)
        ->usingBlockKitTemplate($template);
}
```

### Slack 交互功能

Slack 的 Block Kit 通知系统提供强大的功能来 **处理用户交互**。要使用这些功能，你的 Slack App 需要启用 “Interactivity” 并配置一个 “Request URL”，该 URL 由你的应用提供服务。可以在 Slack 的 App 管理页面的 “Interactivity & Shortcuts” 标签下进行设置。

在下面的示例中，使用了 `actionsBlock` 方法，Slack 会向你的 “Request URL” 发送一个 `POST` 请求，负载中包含点击按钮的 Slack 用户、按钮 ID 等信息。你的应用可以根据负载决定要执行的操作。同时，你应该 **验证请求** 是由 Slack 发出的：[验证来自 Slack 的请求](https://api.slack.com/authentication/verifying-requests-from-slack)：

```php
use Illuminate\Notifications\Slack\BlockKit\Blocks\ActionsBlock;
use Illuminate\Notifications\Slack\BlockKit\Blocks\ContextBlock;
use Illuminate\Notifications\Slack\BlockKit\Blocks\SectionBlock;
use Illuminate\Notifications\Slack\SlackMessage;

/**
 * 获取通知的 Slack 表示
 */
public function toSlack(object $notifiable): SlackMessage
{
    return (new SlackMessage)
        ->text('One of your invoices has been paid!')
        ->headerBlock('Invoice Paid')
        ->contextBlock(function (ContextBlock $block) {
            $block->text('Customer #1234');
        })
        ->sectionBlock(function (SectionBlock $block) {
            $block->text('An invoice has been paid.');
        })
        ->actionsBlock(function (ActionsBlock $block) {
             // ID defaults to "button_acknowledge_invoice"...
            $block->button('Acknowledge Invoice')->primary();

            // Manually configure the ID...
            $block->button('Deny')->danger()->id('deny_invoice');
        });
}
```



### 确认模态框

如果你希望用户在执行某个操作之前必须进行确认，你可以在定义按钮时调用 `confirm` 方法。
`confirm` 方法接收一条消息和一个闭包（closure），该闭包会收到一个 `ConfirmObject` 实例：

```php
use Illuminate\Notifications\Slack\BlockKit\Blocks\ActionsBlock;
use Illuminate\Notifications\Slack\BlockKit\Blocks\ContextBlock;
use Illuminate\Notifications\Slack\BlockKit\Blocks\SectionBlock;
use Illuminate\Notifications\Slack\BlockKit\Composites\ConfirmObject;
use Illuminate\Notifications\Slack\SlackMessage;

/**
 * 将通知转换为 Slack 消息。
 */
public function toSlack(object $notifiable): SlackMessage
{
    return (new SlackMessage)
        ->text('One of your invoices has been paid!')
        ->headerBlock('Invoice Paid')
        ->contextBlock(function (ContextBlock $block) {
            $block->text('Customer #1234');
        })
        ->sectionBlock(function (SectionBlock $block) {
            $block->text('An invoice has been paid.');
        })
        ->actionsBlock(function (ActionsBlock $block) {
            $block->button('Acknowledge Invoice')
                ->primary()
                ->confirm(
                    'Acknowledge the payment and send a thank you email?',
                    function (ConfirmObject $dialog) {
                        $dialog->confirm('Yes');
                        $dialog->deny('No');
                    }
                );
        });
}
```

### 检查 Slack Blocks

如果你想快速检查自己构建的 blocks，可以在 `SlackMessage` 实例上调用 `dd` 方法。
`dd` 方法会生成并输出一个指向 Slack [Block Kit Builder](https://app.slack.com/block-kit-builder/) 的 URL，该工具能在浏览器中展示载荷和通知的预览。
你可以向 `dd` 方法传入 `true`，以输出原始载荷：

```php
return (new SlackMessage)
    ->text('One of your invoices has been paid!')
    ->headerBlock('Invoice Paid')
    ->dd();
```



### 路由 Slack 通知

要将 Slack 通知定向到合适的 Slack 团队和频道，可以在可通知（notifiable）模型上定义一个 `routeNotificationForSlack` 方法。
这个方法可以返回以下三种值之一：

-   `null` —— 将路由交给通知本身配置的频道处理。你可以在构建 `SlackMessage` 时使用 `to` 方法，在通知内部配置频道。

-   一个字符串，指定要发送通知的 Slack 频道，例如 `#support-channel`。

-   一个 `SlackRoute` 实例，它允许你指定一个 OAuth token 和频道名称，例如：`SlackRoute::make($this->slack_channel, $this->slack_token)`。
    这种方式应用于向外部工作区发送通知。

例如，如果在 `routeNotificationForSlack` 方法中返回 `#support-channel`，则通知会被发送到与你的应用程序 `services.php` 配置文件中 **Bot User OAuth token** 相关联的工作区里的 `#support-channel` 频道：

```php
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Illuminate\Notifications\Notification;

class User extends Authenticatable
{
    use Notifiable;

    /**
     * 为 Slack 频道路由通知。
     */
    public function routeNotificationForSlack(Notification $notification): mixed
    {
        return '#support-channel';
    }
}
```

### 通知外部 Slack 工作区 (Notifying External Slack Workspaces)

> [!注意]
> 在向外部 Slack 工作区发送通知之前，你的 Slack 应用必须先[完成分发](#slack-app-distribution)。

当然，你经常会想要将通知发送到属于你应用用户的 Slack 工作区。
为此，你首先需要获取该用户的 Slack OAuth token。
幸运的是，[Laravel Socialite](/docs/laravel/12.x/socialite) 包含一个 Slack 驱动，它可以让你轻松地将你应用的用户与 Slack 进行认证，并[获取一个 bot token](/docs/laravel/12.x/socialite#slack-bot-scopes)。



一旦你获取了 bot token 并将其存储到应用程序的数据库中，你就可以使用 `SlackRoute::make` 方法将通知路由到用户的工作区。
此外，你的应用程序通常还需要提供机会，让用户指定通知应当发送到哪个频道：

```php
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Illuminate\Notifications\Notification;
use Illuminate\Notifications\Slack\SlackRoute;

class User extends Authenticatable
{
    use Notifiable;

    /**
     * 为 Slack 频道路由通知。
     */
    public function routeNotificationForSlack(Notification $notification): mixed
    {
        return SlackRoute::make($this->slack_channel, $this->slack_token);
    }
}
```

## 本地化通知

Laravel 允许你在发送通知时使用不同于 HTTP 请求当前语言环境的 locale，并且如果通知被放入队列，Laravel 甚至会记住这个 locale。

为此，`Illuminate\Notifications\Notification` 类提供了一个 `locale` 方法，用来设置所需的语言。
当通知被评估时，应用程序会切换到该 locale，并在评估完成后恢复到之前的 locale：

```php
$user->notify((new InvoicePaid($invoice))->locale('es'));
```

对于多个可通知实体的本地化，也可以通过 `Notification` facade 来实现：

```php
Notification::locale('es')->send(
    $users, new InvoicePaid($invoice)
);
```

### 用户首选语言环境

有时，应用程序会为每个用户存储其首选的 locale。
通过在你的可通知模型上实现 `HasLocalePreference` 合约，你可以指示 Laravel 在发送通知时使用这个存储的 locale：

```php
use Illuminate\Contracts\Translation\HasLocalePreference;

class User extends Model implements HasLocalePreference
{
    /**
     * 获取用户的首选语言环境。
     */
    public function preferredLocale(): string
    {
        return $this->locale;
    }
}
```



一旦你实现了该接口，Laravel 在向模型发送通知和邮件时会自动使用首选语言环境（locale）。
因此，在使用该接口时，无需手动调用 `locale` 方法：

```php
$user->notify(new InvoicePaid($invoice));
```

## 测试（Testing）

你可以使用 `Notification` facade 的 `fake` 方法来阻止通知实际发送。
通常，发送通知与实际测试的代码无关。大多数情况下，只需断言 Laravel 收到了发送指定通知的指令即可。

在调用 `Notification::fake()` 方法后，你可以断言通知被指示发送给哪些用户，甚至检查通知接收到的数据：

```php tab=Pest
<?php

use App\Notifications\OrderShipped;
use Illuminate\Support\Facades\Notification;

test('orders can be shipped', function () {
    Notification::fake();

    // 执行订单发货操作...

    // 断言没有通知被发送...
    Notification::assertNothingSent();

    // 断言通知已发送给指定用户...
    Notification::assertSentTo(
        [$user], OrderShipped::class
    );

    // 断言通知未发送给某些用户...
    Notification::assertNotSentTo(
        [$user], AnotherNotification::class
    );

    // 断言已发送的通知数量...
    Notification::assertCount(3);
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use App\Notifications\OrderShipped;
use Illuminate\Support\Facades\Notification;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_orders_can_be_shipped(): void
    {
        Notification::fake();

        // 执行订单发货操作...

        // 断言没有通知被发送...
        Notification::assertNothingSent();

        // 断言通知已发送给指定用户...
        Notification::assertSentTo(
            [$user], OrderShipped::class
        );

        // 断言通知未发送给某些用户...
        Notification::assertNotSentTo(
            [$user], AnotherNotification::class
        );

        // 断言已发送的通知数量...
        Notification::assertCount(3);
    }
}
```



你可以向 `assertSentTo` 或 `assertNotSentTo` 方法传递一个闭包，用来断言某个通过指定“真值测试（truth test）”的通知已被发送。
如果至少有一个通知通过了给定的真值测试，那么断言就会成功：

```php
Notification::assertSentTo(
    $user,
    function (OrderShipped $notification, array $channels) use ($order) {
        return $notification->order->id === $order->id;
    }
);
```

#### 按需通知

如果你正在测试的代码发送了[按需通知](#on-demand-notifications)，你可以通过 `assertSentOnDemand` 方法来测试按需通知是否已被发送：

```php
Notification::assertSentOnDemand(OrderShipped::class);
```

通过将一个闭包作为第二个参数传递给 `assertSentOnDemand` 方法，你可以判断按需通知是否被发送到了正确的“路由”地址：

```php
Notification::assertSentOnDemand(
    OrderShipped::class,
    function (OrderShipped $notification, array $channels, object $notifiable) use ($user) {
        return $notifiable->routes['mail'] === $user->email;
    }
);
```

## 通知事件

#### 通知发送事件

当一个通知正在发送时，通知系统会派发 `Illuminate\Notifications\Events\NotificationSending` 事件。
这个事件包含了“可通知”实体和通知实例本身。
你可以在应用程序中为该事件创建[事件监听器](/docs/laravel/12.x/events)：

```php
use Illuminate\Notifications\Events\NotificationSending;

class CheckNotificationStatus
{
    /**
     * 处理事件。
     */
    public function handle(NotificationSending $event): void
    {
        // ...
    }
}
```

如果某个 `NotificationSending` 事件的事件监听器在其 `handle` 方法中返回 `false`，那么该通知将不会被发送：

```php
/**
 * 处理事件。
 */
public function handle(NotificationSending $event): bool
{
    return false;
}
```

在事件监听器中，你可以通过事件对象上的 `notifiable`、`notification` 和 `channel` 属性来获取更多关于通知接收者或通知本身的信息：

```php
/**
 * 处理事件。
 */
public function handle(NotificationSending $event): void
{
    // $event->channel
    // $event->notifiable
    // $event->notification
}
```



#### 通知已发送事件

当一个通知被发送时，通知系统会派发 `Illuminate\Notifications\Events\NotificationSent` 事件。
该事件包含了“可通知”实体和通知实例本身。
你可以在应用程序中为此事件创建事件监听器：

```php
use Illuminate\Notifications\Events\NotificationSent;

class LogNotification
{
    /**
     * 处理事件。
     */
    public function handle(NotificationSent $event): void
    {
        // ...
    }
}
```

在事件监听器中，你可以通过事件对象上的 `notifiable`、`notification`、`channel` 和 `response` 属性，来获取更多关于通知接收者或通知本身的信息：

```php
/**
 * 处理事件。
 */
public function handle(NotificationSent $event): void
{
    // $event->channel
    // $event->notifiable
    // $event->notification
    // $event->response
}
```

## 自定义频道 (Custom Channels)

Laravel 自带了一些通知频道，但你可能希望编写自己的驱动，通过其他渠道来投递通知。
Laravel 让这一过程变得非常简单。

首先，定义一个包含 `send` 方法的类。
该方法应当接收两个参数：一个 `$notifiable` 和一个 `$notification`。

在 `send` 方法中，你可以调用通知上的方法来获取你的频道能够理解的消息对象，然后以你想要的方式将通知发送到 `$notifiable` 实例：

```php
<?php

namespace App\Notifications;

use Illuminate\Notifications\Notification;

class VoiceChannel
{
    /**
     * 发送给定的通知。
     */
    public function send(object $notifiable, Notification $notification): void
    {
        $message = $notification->toVoice($notifiable);

        // 将通知发送到 $notifiable 实例...
    }
}
```

一旦定义好了通知频道类，你就可以在任何通知的 `via` 方法中返回该类名。
在这个示例中，通知的 `toVoice` 方法可以返回你选择的任意对象，用来表示语音消息。
例如，你可能会定义你自己的 `VoiceMessage` 类来表示这些消息：

```php
<?php

namespace App\Notifications;

use App\Notifications\Messages\VoiceMessage;
use App\Notifications\VoiceChannel;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Notification;

class InvoicePaid extends Notification
{
    use Queueable;

    /**
     * 获取通知频道。
     */
    public function via(object $notifiable): string
    {
        return VoiceChannel::class;
    }

    /**
     * 获取通知的语音表示。
     */
    public function toVoice(object $notifiable): VoiceMessage
    {
        // ...
    }
}
```
