
# 邮件

- [简介](#introduction)
    - [配置](#configuration)
    - [驱动前提条件](#driver-prerequisites)
    - [故障转移配置](#failover-configuration)
    - [轮询配置](#round-robin-configuration)
- [生成可邮寄类](#generating-mailables)
- [编写可邮寄类](#writing-mailables)
    - [配置发件人](#configuring-the-sender)
    - [配置视图](#configuring-the-view)
    - [视图数据](#view-data)
    - [附件](#attachments)
    - [内联附件](#inline-attachments)
    - [可附加对象](#attachable-objects)
    - [邮件头](#headers)
    - [标签和元数据](#tags-and-metadata)
    - [自定义 Symfony 邮件消息](#customizing-the-symfony-message)
- [Markdown 可邮寄类](#markdown-mailables)
    - [生成 Markdown 可邮寄类](#generating-markdown-mailables)
    - [编写 Markdown 邮件消息](#writing-markdown-messages)
    - [自定义组件](#customizing-the-components)
- [发送邮件](#sending-mail)
    - [邮件队列](#queueing-mail)
- [渲染可邮寄类](#rendering-mailables)
    - [在浏览器中预览可邮寄类](#previewing-mailables-in-the-browser)
- [本地化可邮寄类](#localizing-mailables)
- [测试](#testing-mailables)
    - [测试可邮寄类内容](#testing-mailable-content)
    - [测试可邮寄类发送](#testing-mailable-sending)
- [邮件与本地开发](#mail-and-local-development)
- [事件](#events)
- [自定义传输方式](#custom-transports)
    - [其他 Symfony 传输方式](#additional-symfony-transports)

<a name="introduction"></a>
## 简介

发送邮件并不复杂。 Laravel 提供了一个简洁的邮件 API ，由流行的 [Symfony Mailer](https://symfony.com/doc/current/mailer.html) 组件提供支持。 Laravel 和 Symfony Mailer 提供了通过 SMTP 、 Mailgun 、 Postmark 、 Resend 、 Amazon SES 和 `sendmail` 发送邮件的驱动程序，使您能够快速开始通过本地或云服务发送邮件。

<a name="configuration"></a>
### 配置

Laravel 的邮件服务可以通过应用的 `config/mail.php` 配置文件进行配置。 该文件中配置的每个邮件程序都可以拥有自己独特的配置，甚至独特的「传输」方式，允许您的应用使用不同的邮件服务来发送特定的邮件消息。 例如，您的应用可以使用 Postmark 发送事务性邮件，同时使用 Amazon SES 发送批量邮件。

在您的 `mail` 配置文件中，您会找到一个 `mailers` 配置数组。 该数组包含了 Laravel 支持的每种主要邮件驱动 / 传输方式的示例配置条目，而 `default` 配置值决定了当您的应用需要发送邮件消息时将默认使用哪个邮件程序。

<a name="driver-prerequisites"></a>
### 驱动 / 传输前提条件

基于 API 的驱动（例如 Mailgun 、 Postmark 、 Resend 和 MailerSend）通常比通过 SMTP 服务器发送邮件更简单、更快速。 只要可能，我们建议您使用这些驱动之一。

<a name="mailgun-driver"></a>
#### Mailgun 驱动

要使用 Mailgun 驱动，需要通过 Composer 安装 Symfony 的 Mailgun Mailer 传输包：

```shell
composer require symfony/mailgun-mailer symfony/http-client
```

接下来，您需要在应用的 `config/mail.php` 配置文件中进行两处更改。 首先，将默认邮件程序设置为 `mailgun` ：

```php
'default' => env('MAIL_MAILER', 'mailgun'),
```

其次，在 `mailers` 数组中添加以下配置：

```php
'mailgun' => [
    'transport' => 'mailgun',
    // 'client' => [
    //     'timeout' => 5,
    // ],
],
```

配置应用的默认邮件程序后，将以下选项添加到 `config/services.php` 配置文件：

```php
'mailgun' => [
    'domain' => env('MAILGUN_DOMAIN'),
    'secret' => env('MAILGUN_SECRET'),
    'endpoint' => env('MAILGUN_ENDPOINT', 'api.mailgun.net'),
    'scheme' => 'https',
],
```

如果您不使用美国 [Mailgun 区域](https://documentation.mailgun.com/en/latest/api-intro.html#mailgun-regions) ，可以在 `services` 配置文件中定义您区域的端点：

```php
'mailgun' => [
    'domain' => env('MAILGUN_DOMAIN'),
    'secret' => env('MAILGUN_SECRET'),
    'endpoint' => env('MAILGUN_ENDPOINT', 'api.eu.mailgun.net'),
    'scheme' => 'https',
],
```

<a name="postmark-driver"></a>

#### Postmark 驱动

要使用 [Postmark](https://postmarkapp.com/) 驱动，需要通过 Composer 安装 Symfony 的 Postmark Mailer 传输包：

```shell
composer require symfony/postmark-mailer symfony/http-client
```

接下来，在应用程序的 `config/mail.php` 配置文件中将 `default`  选项设置为  `postmark`。配置完默认邮件发送器后，请确保 `config/services.php` 配置文件中包含以下选项：

```php
'postmark' => [
    'token' => env('POSTMARK_TOKEN'),
],
```

如果你想为特定邮件发送器指定 Postmark 消息流，可以在邮件发送器的配置数组中添加 `message_stream_id` 配置选项。该配置数组位于应用程序的 `config/mail.php` 配置文件中：

```php
'postmark' => [
    'transport' => 'postmark',
    'message_stream_id' => env('POSTMARK_MESSAGE_STREAM_ID'),
    // 'client' => [
    //     'timeout' => 5,
    // ],
],
```

这样你还可以设置多个使用不同消息流的 Postmark 邮件发送器。

<a name="resend-driver"></a>
#### Resend 驱动

要使用 [Resend](https://resend.com/) 驱动，需要通过 Composer 安装 Resend 的 PHP SDK：

```shell
composer require resend/resend-php
```

接下来，在应用程序的 `config/mail.php` 配置文件中将 `default` 选项设置为 `resend` 。配置完默认邮件发送器后，请确保 `config/services.php` 配置文件中包含以下选项：

```php
'resend' => [
    'key' => env('RESEND_KEY'),
],
```

<a name="ses-driver"></a>
#### SES 驱动

要使用 Amazon SES 驱动，首先需要安装 Amazon AWS SDK for PHP。你可以通过 Composer 包管理器安装这个库：

```shell
composer require aws/aws-sdk-php
```

接下来，在 `config/mail.php` 配置文件中将 `default` 选项设置为 `ses` ，并确保 `config/services.php` 配置文件中包含以下选项：

```php
'ses' => [
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
],
```



要使用 AWS [临时凭证](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_use-resources.html) 通过会话令牌进行身份验证，可以在应用程序的 SES 配置中添加 `token` 键：

```php
'ses' => [
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'token' => env('AWS_SESSION_TOKEN'),
],
```

若要使用 SES 的 [订阅管理功能](https://docs.aws.amazon.com/ses/latest/dg/sending-email-subscription-management.html)，可以在邮件消息的 [headers](#headers) 方法返回的数组中包含 `X-Ses-List-Management-Options` 头信息：

```php
/**
 * Get the message headers.
 */
public function headers(): Headers
{
    return new Headers(
        text: [
            'X-Ses-List-Management-Options' => 'contactListName=MyContactList;topicName=MyTopic',
        ],
    );
}
```

如果需要定义 Laravel 在发送邮件时应传递给 AWS SDK `SendEmail` 方法的 [额外选项](https://docs.aws.amazon.com/aws-sdk-php/v3/api/api-sesv2-2019-09-27.html#sendemail) ，可以在  `ses` 配置中定义 `options` 数组：

```php
'ses' => [
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'options' => [
        'ConfigurationSetName' => 'MyConfigurationSet',
        'EmailTags' => [
            ['Name' => 'foo', 'Value' => 'bar'],
        ],
    ],
],
```

<a name="mailersend-driver"></a>
#### MailerSend 驱动

[MailerSend](https://www.mailersend.com/)作为一款事务性邮件和短信服务，为 Laravel 维护了专门的 API 邮件驱动包。可以通过 Composer 安装该驱动包：

```shell
composer require mailersend/laravel-driver
```

安装完成后，在应用程序的 `.env` 文件中添加 `MAILERSEND_API_KEY` 环境变量。同时需要将 `MAIL_MAILER` 环境变量定义为  `mailersend`:

```ini
MAIL_MAILER=mailersend
MAIL_FROM_ADDRESS=app@yourdomain.com
MAIL_FROM_NAME="App Name"

MAILERSEND_API_KEY=your-api-key
```



最后，在应用程序的 `config/mail.php` 配置文件的 `mailers` 数组中添加 MailerSend 配置：

```php
'mailersend' => [
    'transport' => 'mailersend',
],
```

要了解更多关于 MailerSend 的信息，包括如何使用托管模板，请参阅  [MailerSend 驱动文件](https://github.com/mailersend/mailersend-laravel-driver#usage)。

<a name="failover-configuration"></a>
### 故障转移配置

当您配置的外部邮件服务不可用时，定义备用邮件发送配置会非常有用。要实现这一点，您应该在应用程序的  `mail` 配置文件中定义一个使用 `failover` 传输的邮件发送器。 `failover` 邮件发送器的配置数组应包含一个 `mailers` 数组，指定在主要驱动不可用时按顺序尝试的备用邮件发送器：

```php
'mailers' => [
    'failover' => [
        'transport' => 'failover',
        'mailers' => [
            'postmark',
            'mailgun',
            'sendmail',
        ],
    ],

    // ...
],
```

定义故障转移邮件发送器后，您应该将其设置为应用程序的默认邮件发送器，方法是在 `mail` 配置文件的 `default` 配置键中指定其名称：

```php
'default' => env('MAIL_MAILER', 'failover'),
```

<a name="round-robin-configuration"></a>
### 轮询配置

`roundrobin` 传输允许您将邮件发送工作负载分配到多个邮件发送器上。要开始使用，首先在应用程序的 `mail` 配置文件中定义一个使用 `roundrobin` 传输的邮件发送器。 `roundrobin` 邮件发送器的配置数组应包含一个 `mailers` 数组，指定用于发送邮件的邮件发送器：


```php
'mailers' => [
    'roundrobin' => [
        'transport' => 'roundrobin',
        'mailers' => [
            'ses',
            'postmark',
        ],
    ],

    // ...
],
```



定义轮询邮件程序后，您应通过在其应用的 `mail` 配置文件的 `default` 配置键中指定其名称，将此邮件程序设置为应用使用的默认邮件程序：

```php
'default' => env('MAIL_MAILER', 'roundrobin'),
```

轮询传输会从已配置的邮件程序列表中随机选择一个邮件程序，然后在后续每封邮件中切换到下一个可用邮件程序。 与旨在实现 *[高可用性](https://en.wikipedia.org/wiki/High_availability)* 的 `failover` 传输不同， `roundrobin` 传输提供的是 *[负载均衡](https://en.wikipedia.org/wiki/Load_balancing_(computing))* 。

<a name="generating-mailables"></a>
## 生成可邮寄类

在构建 Laravel 应用时，应用发送的每种邮件类型都表示为一个「可邮寄」类。 这些类存储在 `app/Mail` 目录中。 如果您在应用中没有看到此目录，不必担心，因为它会在您使用 `make:mail` Artisan 命令创建第一个可邮寄类时自动生成：

```shell
php artisan make:mail OrderShipped
```

<a name="writing-mailables"></a>
## 编写可邮寄类

生成可邮寄类后，打开它以便我们可以查看其内容。 可邮寄类的配置通过多个方法完成，包括 `envelope` 、 `content`  和 `attachments`  方法。

`envelope` 方法返回一个 `Illuminate\Mail\Mailables\Envelope` 对象，该对象定义了邮件主题，有时还包括收件人。 `content` 方法返回一个 `Illuminate\Mail\Mailables\Content` 对象，该对象定义了用于生成邮件内容的 [Blade 模板](https://laravel.com/docs/laravel/12.x/blade) 。

<a name="configuring-the-sender"></a>
### 配置发件人

<a name="using-the-envelope"></a>
#### 使用信封配置

首先，让我们来探索如何配置邮件的发件人。 或者说，邮件将「来自」谁。 有两种方式可以配置发件人。 首先，您可以在消息的信封上指定「发件人」地址：

```php
use Illuminate\Mail\Mailables\Address;
use Illuminate\Mail\Mailables\Envelope;

/**
 * 获取消息信封
 */
public function envelope(): Envelope
{
    return new Envelope(
        from: new Address('jeffrey@example.com', 'Jeffrey Way'),
        subject: '订单已发货',
    );
}
```

如果您愿意，也可以指定一个 `replyTo` 地址：

```php
return new Envelope(
    from: new Address('jeffrey@example.com', 'Jeffrey Way'),
    replyTo: [
        new Address('taylor@example.com', 'Taylor Otwell'),
    ],
    subject: '订单已发货',
);
```

<a name="using-a-global-from-address"></a>
#### 使用全局 `from` 地址

但是，如果您的应用对所有邮件使用相同的「发件人」地址，将其添加到每个生成的可邮寄类中可能会变得繁琐。 相反，您可以在 `config/mail.php` 配置文件中指定一个全局「发件人」地址。 如果在可邮寄类中没有指定其他「发件人」地址，则将使用此地址：

```php
'from' => [
    'address' => env('MAIL_FROM_ADDRESS', 'hello@example.com'),
    'name' => env('MAIL_FROM_NAME', 'Example'),
],
```

此外，您可以在 `config/mail.php` 配置文件中定义全局「reply_to」地址：

```php
'reply_to' => ['address' => 'example@example.com', 'name' => '应用名称'],
```

<a name="configuring-the-view"></a>
### 配置视图

在可邮寄类的 `content` 方法中，您可以定义 `view` ，即渲染邮件内容时应使用哪个模板。 由于每封邮件通常使用 [Blade 模板](https://laravel.com/docs/laravel/12.x/blade) 来渲染其内容，因此在构建邮件的 HTML 时，您可以充分利用 Blade 模板引擎的全部功能和便利性：

```php
/**
 * 获取消息内容定义
 */
public function content(): Content
{
    return new Content(
        view: 'mail.orders.shipped',
    );
}
```

> [!注意]
> 您可能希望创建一个 `resources/views/emails` 目录来存放所有的邮件模板； 但是，您也可以自由地将它们放在 `resources/views` 目录中的任何位置。

<a name="plain-text-emails"></a>
#### 纯文本邮件

如果您需要定义邮件的纯文本版本，可以在创建消息的 `Content` 定义时指定纯文本模板。 与 `view` 参数类似， `text` 参数应该是一个模板名称，用于渲染邮件的纯文本内容。 您可以自由定义邮件的 HTML 和纯文本版本：

```php
/**
 * 获取消息内容定义
 */
public function content(): Content
{
    return new Content(
        view: 'mail.orders.shipped',
        text: 'mail.orders.shipped-text'
    );
}
```

为了更清晰，可以使用 `html` 参数作为 `view` 参数的别名：

```php
return new Content(
    html: 'mail.orders.shipped',
    text: 'mail.orders.shipped-text'
);
```

<a name="view-data"></a>
### 视图数据

<a name="via-public-properties"></a>
#### 通过公共属性传递

通常，您会希望向视图传递一些数据，以便在渲染邮件的 HTML 时使用。 有两种方法可以让数据在视图中可用。 首先，在可邮寄类上定义的任何公共属性都会自动提供给视图使用。 因此，例如，您可以将数据传递到可邮寄类的构造函数中，并将这些数据设置为类上定义的公共属性：

```php
<?php

namespace App\Mail;

use App\Models\Order;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Queue\SerializesModels;

class OrderShipped extends Mailable
{
    use Queueable, SerializesModels;

    /**
     * 创建新消息实例
     */
    public function __construct(
        public Order $order,
    ) {}

    /**
     * 获取消息内容定义
     */
    public function content(): Content
    {
        return new Content(
            view: 'mail.orders.shipped',
        );
    }
}
```

一旦数据被设置为公共属性，它将自动在您的视图中可用，因此您可以像访问Blade模板中的任何其他数据一样访问它：

```blade
<div>
    Price: {{ $order->price }}
</div>
```

<a name="via-the-with-parameter"></a>
#### 通过 `with` 参数传递:

如果您想在将电子邮件数据发送到模板之前自定义其格式，您可以通过 `Content` 定义的 `with` 参数手动将数据传递给视图。通常，您仍将通过mailable类的构造函数传递数据；但是，您应该将此数据设置为 `protected` 或 `private` 属性，这样数据就不会自动提供给模板：

```php
<?php

namespace App\Mail;

use App\Models\Order;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Queue\SerializesModels;

class OrderShipped extends Mailable
{
    use Queueable, SerializesModels;

    /**
     * Create a new message instance.
     */
    public function __construct(
        protected Order $order,
    ) {}

    /**
     * Get the message content definition.
     */
    public function content(): Content
    {
        return new Content(
            view: 'mail.orders.shipped',
            with: [
                'orderName' => $this->order->name,
                'orderPrice' => $this->order->price,
            ],
        );
    }
}
```

数据通过 `with` 方法传递后，会自动在视图中可用，您可以像访问Blade模板中的其他数据一样访问它：

```blade
<div>
    Price: {{ $orderPrice }}
</div>
```

<a name="attachments"></a>
### 附件

要为邮件添加附件，您需要在消息的 `attachments` 方法返回的数组中添加附件。首先，您可以通过 `Attachment` 类提供的 `fromPath` 方法添加文件路径来附加文件：

```php
use Illuminate\Mail\Mailables\Attachment;

/**
 * Get the attachments for the message.
 *
 * @return array<int, \Illuminate\Mail\Mailables\Attachment>
 */
public function attachments(): array
{
    return [
        Attachment::fromPath('/path/to/file'),
    ];
}
```



为邮件添加附件时，您还可以通过 `as` 和 `withMime` 方法分别指定附件的显示名称和MIME类型：

```php
/**
 * Get the attachments for the message.
 *
 * @return array<int, \Illuminate\Mail\Mailables\Attachment>
 */
public function attachments(): array
{
    return [
        Attachment::fromPath('/path/to/file')
            ->as('name.pdf')
            ->withMime('application/pdf'),
    ];
}
```

<a name="attaching-files-from-disk"></a>
#### 从存储磁盘附加文件

如果文件已存储在某个 [文件系统磁盘](/docs/laravel/12.x/filesystem)上，可以使用 `fromStorage` 方法附加：

```php
/**
 * Get the attachments for the message.
 *
 * @return array<int, \Illuminate\Mail\Mailables\Attachment>
 */
public function attachments(): array
{
    return [
        Attachment::fromStorage('/path/to/file'),
    ];
}
```

当然，您也可以指定附件的名称和MIME类型：

```php
/**
 * Get the attachments for the message.
 *
 * @return array<int, \Illuminate\Mail\Mailables\Attachment>
 */
public function attachments(): array
{
    return [
        Attachment::fromStorage('/path/to/file')
            ->as('name.pdf')
            ->withMime('application/pdf'),
    ];
}
```

如需使用非默认存储磁盘，可使用 `fromStorageDisk` 方法：

```php
/**
 * Get the attachments for the message.
 *
 * @return array<int, \Illuminate\Mail\Mailables\Attachment>
 */
public function attachments(): array
{
    return [
        Attachment::fromStorageDisk('s3', '/path/to/file')
            ->as('name.pdf')
            ->withMime('application/pdf'),
    ];
}
```

<a name="raw-data-attachments"></a>
#### 原始数据附件

`fromData` 方法允许将字节字符串作为附件添加。例如，当您已在内存中生成PDF文件且不希望写入磁盘时，可以使用此方法。该方法接收一个返回原始数据的闭包，以及附件名称：

```php
/**
 * Get the attachments for the message.
 *
 * @return array<int, \Illuminate\Mail\Mailables\Attachment>
 */
public function attachments(): array
{
    return [
        Attachment::fromData(fn () => $this->pdf, 'Report.pdf')
            ->withMime('application/pdf'),
    ];
}
```



### 内联附件

将内联图片嵌入到邮件中通常比较麻烦；不过，Laravel 提供了一种方便的方法来将图片附加到邮件中。要嵌入内联图片，可以在邮件模板中对 `$message` 变量调用 `embed` 方法。Laravel 会自动将 `$message` 变量传递给所有的邮件模板，因此你无需手动传入它：

```blade
<body>
    这里是一张图片：

    <img src="{{ $message->embed($pathToImage) }}">
</body>
```

> [!警告]
> `$message` 变量在纯文本消息模板中不可用，因为纯文本消息不支持内联附件。

#### 嵌入原始数据附件

如果你已经有一段原始的图片数据字符串，并希望将它嵌入到邮件模板中，可以对 `$message` 变量调用 `embedData` 方法。在调用 `embedData` 方法时，你需要提供一个文件名，该文件名将分配给嵌入的图片：

```blade
<body>
     这里是一张来自原始数据的图片：

    <img src="{{ $message->embedData($data, 'example-image.jpg') }}">
</body>
```

### 可附加对象

虽然通过字符串路径将文件附加到消息中通常已经足够，但在很多情况下，应用程序中的可附加实体是由类表示的。比如，如果你的应用程序需要将一张照片附加到消息中，你的应用程序中可能也有一个代表该照片的 `Photo` 模型。在这种情况下，如果能直接将 `Photo` 模型传递给 `attach` 方法，那就非常方便了。可附加对象正是为了实现这种功能而存在的。



要开始使用时，可以在需要附加到消息中的对象上实现 `Illuminate\Contracts\Mail\Attachable` 接口。
该接口要求你的类定义一个 `toMailAttachment` 方法，并返回一个 `Illuminate\Mail\Attachment` 实例：

```php
<?php

namespace App\Models;

use Illuminate\Contracts\Mail\Attachable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Mail\Attachment;

class Photo extends Model implements Attachable
{
    /**
     * 获取模型的可附加表示
     */
    public function toMailAttachment(): Attachment
    {
        return Attachment::fromPath('/path/to/file');
    }
}
```

一旦你定义了可附加对象，就可以在构建邮件消息时，从 `attachments` 方法中返回该对象的实例：

```php
/**
 * 获取消息的附件
 *
 * @return array<int, \Illuminate\Mail\Mailables\Attachment>
 */
public function attachments(): array
{
    return [$this->photo];
}
```

当然，附件数据也可能存储在远程文件存储服务（如 Amazon S3）中。因此，Laravel 也允许你基于应用程序的 [文件系统磁盘](/docs/laravel/12.x/filesystem) 来生成附件实例：

```php
// 从默认磁盘上的文件创建一个附件...
return Attachment::fromStorage($this->path);

// 从指定磁盘上的文件创建一个附件...
return Attachment::fromStorageDisk('backblaze', $this->path);
```

此外，你还可以通过内存中的数据来创建附件实例。
为此，可以向 `fromData` 方法传递一个闭包，该闭包应返回表示附件的原始数据：

```php
return Attachment::fromData(fn () => $this->content, 'Photo Name');
```

Laravel 还提供了额外的方法，用于自定义附件。
例如，你可以使用 `as` 和 `withMime` 方法来自定义文件的名称和 MIME 类型：

```php
return Attachment::fromPath('/path/to/file')
    ->as('Photo Name')
    ->withMime('image/jpeg');
```



### 头信息（Headers）

有时候，你可能需要为要发送的邮件附加额外的头信息。例如，你可能需要设置一个自定义的 `Message-Id`，或者其他任意的文本头。

要实现这一点，可以在 mailable 类上定义一个 `headers` 方法。
`headers` 方法应该返回一个 `Illuminate\Mail\Mailables\Headers` 实例。这个类接收 `messageId`、`references` 和 `text` 参数。当然，你只需要提供适合你特定邮件所需的参数即可：

```php
use Illuminate\Mail\Mailables\Headers;

/**
 * 获取邮件头信息
 */
public function headers(): Headers
{
    return new Headers(
        messageId: 'custom-message-id@example.com',
        references: ['previous-message@example.com'],
        text: [
            'X-Custom-Header' => 'Custom Value',
        ],
    );
}
```

### 标签与元数据（Tags and Metadata）

一些第三方邮件服务商（如 Mailgun 和 Postmark）支持邮件的“标签”（tags）和“元数据”（metadata），这些功能可用于对应用程序发送的邮件进行分组和追踪。
你可以通过 `Envelope` 定义为邮件添加标签和元数据：

```php
use Illuminate\Mail\Mailables\Envelope;

/**
 * 获取邮件信封
 *
 * @return \Illuminate\Mail\Mailables\Envelope
 */
public function envelope(): Envelope
{
    return new Envelope(
        subject: 'Order Shipped',
        tags: ['shipment'],
        metadata: [
            'order_id' => $this->order->id,
        ],
    );
}
```

如果你的应用程序使用的是 Mailgun 驱动，可以参考 Mailgun 的文档以获取关于 [标签](https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/?utm_source=chatgpt.com#tagging) 和 [元数据](https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/?utm_source=chatgpt.com#attaching-data-to-messages) 的更多信息。
同样地，你也可以参考 Postmark 的文档，了解其对 [标签](https://postmarkapp.com/blog/tags-support-for-smtp?utm_source=chatgpt.com) 和 [元数据](https://postmarkapp.com/support/article/1125-custom-metadata-faq?utm_source=chatgpt.com) 的支持。



如果你的应用程序使用 Amazon SES 来发送邮件，那么你应该使用 `metadata` 方法将 [SES “标签”](https://docs.aws.amazon.com/ses/latest/APIReference/API_MessageTag.html?utm_source=chatgpt.com) 附加到消息中。

### 自定义 Symfony 消息

Laravel 的邮件功能由 Symfony Mailer 提供支持。Laravel 允许你注册自定义回调，这些回调会在发送消息之前，通过 Symfony 的 Message 实例来执行。这样你就有机会在消息真正发送前对其进行深度定制。

要实现这一点，可以在 `Envelope` 定义中添加一个 `using` 参数：

```php
use Illuminate\Mail\Mailables\Envelope;
use Symfony\Component\Mime\Email;

/**
 * 获取邮件信封
 */
public function envelope(): Envelope
{
    return new Envelope(
        subject: 'Order Shipped',
        using: [
            function (Email $message) {
                // ...
            },
        ]
    );
}
```

## Markdown 邮件类（Markdown Mailables）

Markdown 邮件类允许你在自定义 mailable 中，使用 [邮件通知](/docs/laravel/12.x/notifications#mail-notifications) 中预构建的模板和组件。
由于这些消息是用 Markdown 编写的，Laravel 能够渲染出美观、响应式的 HTML 模板，并且自动生成对应的纯文本版本。

### 生成 Markdown 邮件类

要生成带有 Markdown 模板的 mailable，可以使用 `make:mail` Artisan 命令的 `--markdown` 选项：

```shell
php artisan make:mail OrderShipped --markdown=mail.orders.shipped
```

然后，在邮件类中配置 `content` 方法时，应当使用 `markdown` 参数，而不是 `view` 参数：

```php
use Illuminate\Mail\Mailables\Content;

/**
 * 获取消息内容定义
 */
public function content(): Content
{
    return new Content(
        markdown: 'mail.orders.shipped',
        with: [
            'url' => $this->orderUrl,
        ],
    );
}
```



### 编写 Markdown 消息

Markdown 邮件类结合了 Blade 组件和 Markdown 语法，让你能够轻松构建邮件消息，同时还能利用 Laravel 内置的邮件 UI 组件：

```blade
<x-mail::message>
# Order Shipped

Your order has been shipped!

<x-mail::button :url="$url">
View Order
</x-mail::button>

Thanks,<br>
{{ config('app.name') }}
</x-mail::message>
```

> [!注意]
> 在编写 Markdown 邮件时，不要使用多余的缩进。根据 Markdown 标准，Markdown 解析器会将缩进内容渲染为代码块。

#### 按钮组件（Button Component）

按钮组件会渲染一个居中的按钮链接。
该组件接受两个参数：`url` 和一个可选的 `color`。
支持的颜色有：`primary`、`success` 和 `error`。
你可以在一封邮件中添加任意数量的按钮组件：

```blade
<x-mail::button :url="$url" color="success">
View Order
</x-mail::button>
```

#### 面板组件（Panel Component）

面板组件会将指定的文本块渲染在一个面板中，这个面板的背景颜色与邮件的其余部分略有不同。
这能让你突出显示某一段文本：

```blade
<x-mail::panel>
This is the panel content.
</x-mail::panel>
```

#### 表格组件（Table Component）

表格组件允许你将 Markdown 表格转换为 HTML 表格。
该组件接收 Markdown 表格作为内容。
表格列的对齐方式支持标准 Markdown 表格对齐语法：

```blade
<x-mail::table>
| Laravel       | Table         | Example       |
| ------------- | :-----------: | ------------: |
| Col 2 is      | Centered      | $10           |
| Col 3 is      | Right-Aligned | $20           |
</x-mail::table>
```



### 自定义组件（Customizing the Components）

你可以将所有 Markdown 邮件组件导出到你的应用程序中，以便进行自定义。
要导出组件，可以使用 `vendor:publish` Artisan 命令发布 `laravel-mail` 资源标签：

```shell
php artisan vendor:publish --tag=laravel-mail
```

该命令会将 Markdown 邮件组件发布到 `resources/views/vendor/mail` 目录下。
`mail` 目录中将包含 `html` 和 `text` 两个目录，每个目录中包含每个可用组件的相应表示形式。
你可以自由地对这些组件进行自定义。

#### 自定义 CSS

导出组件后，`resources/views/vendor/mail/html/themes` 目录下会包含一个 `default.css` 文件。
你可以自定义此文件中的 CSS，修改后的样式将自动转换为内联 CSS 样式，并应用到 Markdown 邮件的 HTML 表示中。

如果你想为 Laravel 的 Markdown 组件构建一个全新的主题，可以在 `html/themes` 目录中放置一个 CSS 文件。
命名并保存你的 CSS 文件后，更新应用程序 `config/mail.php` 配置文件中的 `theme` 选项，使其匹配新主题的名称。

要为单个 mailable 自定义主题，可以将 mailable 类的 `$theme` 属性设置为发送该邮件时应使用的主题名称。

## 发送邮件（Sending Mail）

要发送邮件，可以使用 `Mail` [facade](/docs/laravel/12.x/facades) 的 `to` 方法。
`to` 方法可以接受一个邮箱地址、一个用户实例，或一个用户集合。

如果你传递一个对象或对象集合，邮件发送器会自动使用它们的 `email` 和 `name` 属性来确定收件人，因此请确保这些属性在对象中可用。

指定收件人后，可以将 mailable 类的实例传递给 `send` 方法：

```php
<?php

namespace App\Http\Controllers;

use App\Mail\OrderShipped;
use App\Models\Order;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Mail;

class OrderShipmentController extends Controller
{
    /**
     * 发送指定订单
     */
    public function store(Request $request): RedirectResponse
    {
        $order = Order::findOrFail($request->order_id);

        // 处理订单发货...

        Mail::to($request->user())->send(new OrderShipped($order));

        return redirect('/orders');
    }
}
```



发送邮件时，你不仅可以指定 “to” 收件人。
你可以自由地设置 “to”、 “cc” 和 “bcc” 收件人，只需将各自的方法链式调用即可：

```php
Mail::to($request->user())
    ->cc($moreUsers)
    ->bcc($evenMoreUsers)
    ->send(new OrderShipped($order));
```

#### 遍历收件人（Looping Over Recipients）

有时候，你可能需要通过遍历收件人数组 / 邮箱地址列表来发送邮件。
但是，由于 `to` 方法会将邮箱地址追加到 mailable 的收件人列表中，因此每次循环都会向之前的每个收件人再次发送邮件。
因此，你应当为每个收件人重新创建 mailable 实例：

```php
foreach (['taylor@example.com', 'dries@example.com'] as $recipient) {
    Mail::to($recipient)->send(new OrderShipped($order));
}
```

#### 使用特定邮件发送器发送邮件（Sending Mail via a Specific Mailer）

默认情况下，Laravel 会使用应用程序 `mail` 配置文件中设置的 `default` 邮件发送器来发送邮件。
但是，你可以使用 `mailer` 方法指定特定的邮件发送器配置来发送邮件：

```php
Mail::mailer('postmark')
    ->to($request->user())
    ->send(new OrderShipped($order));
```

### 邮件队列（Queueing Mail）

#### 队列发送邮件（Queueing a Mail Message）

由于发送邮件可能会影响应用程序的响应时间，许多开发者选择将邮件放入队列进行后台发送。
Laravel 提供了内置的 [统一队列 API](/docs/laravel/12.x/queues) 来简化这一操作。

要将邮件放入队列发送，可以在指定收件人后，调用 `Mail` facade 的 `queue` 方法：

```php
Mail::to($request->user())
    ->cc($moreUsers)
    ->bcc($evenMoreUsers)
    ->queue(new OrderShipped($order));
```



此方法会自动将任务推送到队列中，以便消息在后台发送。
在使用此功能之前，你需要先[配置你的队列](/docs/laravel/12.x/queues)。

#### 延迟队列发送（Delayed Message Queueing）

如果你希望延迟发送队列中的邮件消息，可以使用 `later` 方法。
`later` 方法的第一个参数接受一个 `DateTime` 实例，用于指定消息应当发送的时间：

```php
Mail::to($request->user())
    ->cc($moreUsers)
    ->bcc($evenMoreUsers)
    ->later(now()->addMinutes(10), new OrderShipped($order));
```

#### 推送到特定队列（Pushing to Specific Queues）

由于通过 `make:mail` 命令生成的所有 mailable 类都使用了 `Illuminate\Bus\Queueable` trait，
因此你可以在任何 mailable 实例上调用 `onQueue` 和 `onConnection` 方法，从而指定消息使用的队列连接和队列名称：

```php
$message = (new OrderShipped($order))
    ->onConnection('sqs')
    ->onQueue('emails');

Mail::to($request->user())
    ->cc($moreUsers)
    ->bcc($evenMoreUsers)
    ->queue($message);
```

#### 默认队列（Queueing by Default）

如果你希望某些 mailable 类始终使用队列发送，可以在类上实现 `ShouldQueue` 接口。
这样，即使你调用 `send` 方法发送邮件，该 mailable 也会被加入队列，因为它实现了该接口：

```php
use Illuminate\Contracts\Queue\ShouldQueue;

class OrderShipped extends Mailable implements ShouldQueue
{
    // ...
}
```

#### 队列邮件与数据库事务（Queued Mailables and Database Transactions）

当队列邮件在数据库事务中被派发时，可能会在数据库事务提交之前就被队列处理。
在这种情况下，你在事务中对模型或数据库记录所做的更新，可能尚未反映到数据库中。
此外，在事务中创建的任何模型或数据库记录，可能还不存在于数据库中。
如果你的 mailable 依赖这些模型，队列任务处理该邮件时可能会发生意外错误。



如果你的队列连接的 `after_commit` 配置选项被设置为 `false`，你仍然可以通过在发送邮件时调用 `afterCommit` 方法，指示某个队列邮件在所有打开的数据库事务提交后才派发：

```php
Mail::to($request->user())->send(
    (new OrderShipped($order))->afterCommit()
);
```

或者，你也可以在 mailable 的构造函数中调用 `afterCommit` 方法：

```php
<?php

namespace App\Mail;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Queue\SerializesModels;

class OrderShipped extends Mailable implements ShouldQueue
{
    use Queueable, SerializesModels;

    /**
     * 创建一个新的邮件实例
     */
    public function __construct()
    {
        $this->afterCommit();
    }
}
```

> [!注意]
> 想要了解更多关于解决这些问题的方法，请参考文档中关于 [队列任务与数据库事务](/docs/laravel/12.x/queues#jobs-and-database-transactions) 的说明。

## 渲染 Mailable（Rendering Mailables）

有时，你可能希望捕获 mailable 的 HTML 内容而不发送它。
为此，你可以调用 mailable 的 `render` 方法。
该方法会返回评估后的 HTML 内容，类型为字符串：

```php
use App\Mail\InvoicePaid;
use App\Models\Invoice;

$invoice = Invoice::find(1);

return (new InvoicePaid($invoice))->render();
```

### 在浏览器中预览 Mailable（Previewing Mailables in the Browser）

在设计 mailable 模板时，能够快速在浏览器中预览渲染后的邮件就像预览普通 Blade 模板一样非常方便。
因此，Laravel 允许你直接从路由闭包或控制器返回任何 mailable。

当返回 mailable 时，它会被渲染并显示在浏览器中，让你可以快速预览设计，而无需发送到真实邮箱：

```php
Route::get('/mailable', function () {
    $invoice = App\Models\Invoice::find(1);

    return new App\Mail\InvoicePaid($invoice);
});
```



## 本地化邮件（Localizing Mailables）

Laravel 允许你在请求的当前语言环境之外发送邮件，并且即使邮件被加入队列，Laravel 也会记住该语言环境。

为此，`Mail` facade 提供了 `locale` 方法来设置所需的语言。
在评估 mailable 模板时，应用程序会切换到该语言环境，评估完成后再恢复到之前的语言环境：

```php
Mail::to($request->user())->locale('es')->send(
    new OrderShipped($order)
);
```

### 用户首选语言（User Preferred Locales）

有时候，应用程序会存储每个用户的首选语言。
通过在一个或多个模型上实现 `HasLocalePreference` 接口，你可以指示 Laravel 在发送邮件时使用存储的首选语言：

```php
use Illuminate\Contracts\Translation\HasLocalePreference;

class User extends Model implements HasLocalePreference
{
    /**
     * 获取用户的首选语言
     */
    public function preferredLocale(): string
    {
        return $this->locale;
    }
}
```

实现该接口后，Laravel 会在向该模型发送邮件或通知时自动使用首选语言。
因此，使用该接口时无需再调用 `locale` 方法：

```php
Mail::to($request->user())->send(new OrderShipped($order));
```

## 测试（Testing）

### 测试 Mailable 内容（Testing Mailable Content）

Laravel 提供了多种方法来检查 mailable 的结构。此外，还提供了一些便捷方法，用于测试你的 mailable 是否包含预期的内容。
这些方法包括：

`assertSeeInHtml`、`assertDontSeeInHtml`、`assertSeeInOrderInHtml`、`assertSeeInText`、`assertDontSeeInText`、`assertSeeInOrderInText`、`assertHasAttachment`、`assertHasAttachedData`、`assertHasAttachmentFromStorage`、`assertHasAttachmentFromStorageDisk`。

如你所料，带 “HTML” 的断言用于检查 mailable 的 HTML 版本是否包含指定字符串，而带 “text” 的断言用于检查纯文本版本是否包含指定字符串：

```php tab=Pest
use App\Mail\InvoicePaid;
use App\Models\User;

test('mailable content', function () {
    $user = User::factory()->create();

    $mailable = new InvoicePaid($user);

    $mailable->assertFrom('jeffrey@example.com');
    $mailable->assertTo('taylor@example.com');
    $mailable->assertHasCc('abigail@example.com');
    $mailable->assertHasBcc('victoria@example.com');
    $mailable->assertHasReplyTo('tyler@example.com');
    $mailable->assertHasSubject('Invoice Paid');
    $mailable->assertHasTag('example-tag');
    $mailable->assertHasMetadata('key', 'value');

    $mailable->assertSeeInHtml($user->email);
    $mailable->assertSeeInHtml('Invoice Paid');
    $mailable->assertSeeInOrderInHtml(['Invoice Paid', 'Thanks']);

    $mailable->assertSeeInText($user->email);
    $mailable->assertSeeInOrderInText(['Invoice Paid', 'Thanks']);

    $mailable->assertHasAttachment('/path/to/file');
    $mailable->assertHasAttachment(Attachment::fromPath('/path/to/file'));
    $mailable->assertHasAttachedData($pdfData, 'name.pdf', ['mime' => 'application/pdf']);
    $mailable->assertHasAttachmentFromStorage('/path/to/file', 'name.pdf', ['mime' => 'application/pdf']);
    $mailable->assertHasAttachmentFromStorageDisk('s3', '/path/to/file', 'name.pdf', ['mime' => 'application/pdf']);
});
```

```php tab=PHPUnit
use App\Mail\InvoicePaid;
use App\Models\User;

public function test_mailable_content(): void
{
    $user = User::factory()->create();

    $mailable = new InvoicePaid($user);

    $mailable->assertFrom('jeffrey@example.com');
    $mailable->assertTo('taylor@example.com');
    $mailable->assertHasCc('abigail@example.com');
    $mailable->assertHasBcc('victoria@example.com');
    $mailable->assertHasReplyTo('tyler@example.com');
    $mailable->assertHasSubject('Invoice Paid');
    $mailable->assertHasTag('example-tag');
    $mailable->assertHasMetadata('key', 'value');

    $mailable->assertSeeInHtml($user->email);
    $mailable->assertSeeInHtml('Invoice Paid');
    $mailable->assertSeeInOrderInHtml(['Invoice Paid', 'Thanks']);

    $mailable->assertSeeInText($user->email);
    $mailable->assertSeeInOrderInText(['Invoice Paid', 'Thanks']);

    $mailable->assertHasAttachment('/path/to/file');
    $mailable->assertHasAttachment(Attachment::fromPath('/path/to/file'));
    $mailable->assertHasAttachedData($pdfData, 'name.pdf', ['mime' => 'application/pdf']);
    $mailable->assertHasAttachmentFromStorage('/path/to/file', 'name.pdf', ['mime' => 'application/pdf']);
    $mailable->assertHasAttachmentFromStorageDisk('s3', '/path/to/file', 'name.pdf', ['mime' => 'application/pdf']);
}
```



### 测试 Mailable 发送（Testing Mailable Sending）

建议将邮件内容的测试与断言某个 mailable 已经“发送”给特定用户的测试分开进行。
通常，mailable 的内容与你正在测试的代码无关，只需要断言 Laravel 指示发送了某个 mailable 即可。

你可以使用 `Mail` facade 的 `fake` 方法来阻止邮件实际发送。
在调用 `Mail::fake()` 后，你可以断言邮件已被指示发送给用户，甚至检查 mailable 接收到的数据：

```php tab=Pest
<?php

use App\Mail\OrderShipped;
use Illuminate\Support\Facades\Mail;

test('orders can be shipped', function () {
    Mail::fake();

    // 执行订单发货操作...

    // 断言没有邮件被发送
    Mail::assertNothingSent();

    // 断言某个 mailable 已发送
    Mail::assertSent(OrderShipped::class);

    // 断言某个 mailable 被发送了两次
    Mail::assertSent(OrderShipped::class, 2);

    // 断言某个 mailable 被发送到指定邮箱
    Mail::assertSent(OrderShipped::class, 'example@laravel.com');

    // 断言某个 mailable 被发送到多个邮箱
    Mail::assertSent(OrderShipped::class, ['example@laravel.com', '...']);

    // 断言某个 mailable 没有被发送
    Mail::assertNotSent(AnotherMailable::class);

    // 断言总共发送了 3 个 mailable
    Mail::assertSentCount(3);
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use App\Mail\OrderShipped;
use Illuminate\Support\Facades\Mail;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    public function test_orders_can_be_shipped(): void
    {
        Mail::fake();

        // 执行订单发货操作...

        // 断言没有邮件被发送
        Mail::assertNothingSent();

        // 断言某个 mailable 已发送
        Mail::assertSent(OrderShipped::class);

        // 断言某个 mailable 被发送了两次
        Mail::assertSent(OrderShipped::class, 2);

        // 断言某个 mailable 被发送到指定邮箱
        Mail::assertSent(OrderShipped::class, 'example@laravel.com');

        // 断言某个 mailable 被发送到多个邮箱
        Mail::assertSent(OrderShipped::class, ['example@laravel.com', '...']);

        // 断言某个 mailable 没有被发送
        Mail::assertNotSent(AnotherMailable::class);

        // 断言总共发送了 3 个 mailable
        Mail::assertSentCount(3);
    }
}
```



如果你将邮件加入队列以在后台发送，应该使用 `assertQueued` 方法，而不是 `assertSent`：

```php
Mail::assertQueued(OrderShipped::class);
Mail::assertNotQueued(OrderShipped::class);
Mail::assertNothingQueued();
Mail::assertQueuedCount(3);
```

你可以向 `assertSent`、`assertNotSent`、`assertQueued` 或 `assertNotQueued` 方法传入一个闭包，以断言发送的 mailable 是否满足某个“条件测试”。
只要至少有一个 mailable 满足给定的条件，断言就会成功：

```php
Mail::assertSent(function (OrderShipped $mail) use ($order) {
    return $mail->order->id === $order->id;
});
```

在调用 `Mail` facade 的断言方法时，闭包接受的 mailable 实例提供了许多有用的方法来检查邮件：

```php
Mail::assertSent(OrderShipped::class, function (OrderShipped $mail) use ($user) {
    return $mail->hasTo($user->email) &&
           $mail->hasCc('...') &&
           $mail->hasBcc('...') &&
           $mail->hasReplyTo('...') &&
           $mail->hasFrom('...') &&
           $mail->hasSubject('...');
});
```

mailable 实例还提供了若干方法来检查邮件附件：

```php
use Illuminate\Mail\Mailables\Attachment;

Mail::assertSent(OrderShipped::class, function (OrderShipped $mail) {
    return $mail->hasAttachment(
        Attachment::fromPath('/path/to/file')
            ->as('name.pdf')
            ->withMime('application/pdf')
    );
});

Mail::assertSent(OrderShipped::class, function (OrderShipped $mail) {
    return $mail->hasAttachment(
        Attachment::fromStorageDisk('s3', '/path/to/file')
    );
});

Mail::assertSent(OrderShipped::class, function (OrderShipped $mail) use ($pdfData) {
    return $mail->hasAttachment(
        Attachment::fromData(fn () => $pdfData, 'name.pdf')
    );
});
```

你可能已经注意到，用于断言邮件未发送的方法有两个：`assertNotSent` 和 `assertNotQueued`。
有时候，你可能希望断言没有邮件被发送 **或** 加入队列。
为此，可以使用 `assertNothingOutgoing` 和 `assertNotOutgoing` 方法：

```php
Mail::assertNothingOutgoing();

Mail::assertNotOutgoing(function (OrderShipped $mail) use ($order) {
    return $mail->order->id === $order->id;
});
```



## 邮件与本地开发（Mail and Local Development）

在开发一个会发送邮件的应用时，你通常不希望邮件真的发送到真实邮箱地址。
Laravel 提供了几种方式，在本地开发环境下“禁用”邮件的实际发送。

### 日志驱动（Log Driver）

`log` 邮件驱动不会发送邮件，而是将所有邮件消息写入日志文件中以便检查。
通常，这个驱动仅在本地开发时使用。
有关根据不同环境配置应用程序的详细信息，请参阅 [配置文档](/docs/laravel/12.x/configuration#environment-configuration)。

### HELO / Mailtrap / Mailpit

或者，你可以使用像 [HELO](https://usehelo.com?utm_source=chatgpt.com) 或 [Mailtrap](https://mailtrap.io?utm_source=chatgpt.com) 的服务，配合 `smtp` 驱动，将邮件发送到一个“虚拟”邮箱，从而可以在真实邮件客户端中查看。
这种方法的好处是，你可以在 Mailtrap 的消息查看器中实际检查最终邮件。

如果你使用 [Laravel Sail](/docs/laravel/12.x/sail)，可以通过 [Mailpit](https://github.com/axllent/mailpit?utm_source=chatgpt.com) 预览邮件。
当 Sail 运行时，你可以通过访问 `http://localhost:8025` 访问 Mailpit 界面。

### 使用全局 “to” 地址（Using a Global `to` Address）

最后，你可以通过调用 `Mail` facade 提供的 `alwaysTo` 方法，指定全局的收件地址。

```php
use Illuminate\Support\Facades\Mail;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    if ($this->app->environment('local')) {
        Mail::alwaysTo('taylor@example.com');
    }
}
```



## 事件（Events）

在发送邮件时，Laravel 会触发两个事件：
-   `MessageSending`：在邮件发送之前触发。
-   `MessageSent`：在邮件发送之后触发。
请注意，这些事件是在邮件 **实际发送** 时触发的，而不是在邮件被加入队列时触发。
你可以在应用中为这些事件创建 [事件监听器](/docs/laravel/12.x/events)：

```php
use Illuminate\Mail\Events\MessageSending;
// use Illuminate\Mail\Events\MessageSent;

class LogMessage
{
    /**
     * 处理事件
     */
    public function handle(MessageSending $event): void
    {
        // ...
    }
}
```

## 自定义传输（Custom Transports）

Laravel 自带多种邮件传输方式，但有时你可能希望为其他 Laravel 默认不支持的服务编写自定义传输。
要开始，定义一个类，继承 `Symfony\Component\Mailer\Transport\AbstractTransport` 类。
然后在你的传输类中实现 `doSend` 和 `__toString()` 方法：

```php
use MailchimpTransactional\ApiClient;
use Symfony\Component\Mailer\SentMessage;
use Symfony\Component\Mailer\Transport\AbstractTransport;
use Symfony\Component\Mime\Address;
use Symfony\Component\Mime\MessageConverter;

class MailchimpTransport extends AbstractTransport
{
    /**
     * 创建新的 Mailchimp 传输实例
     */
    public function __construct(
        protected ApiClient $client,
    ) {
        parent::__construct();
    }

    /**
     * {@inheritDoc}
     */
    protected function doSend(SentMessage $message): void
    {
        $email = MessageConverter::toEmail($message->getOriginalMessage());

        $this->client->messages->send(['message' => [
            'from_email' => $email->getFrom(),
            'to' => collect($email->getTo())->map(function (Address $email) {
                return ['email' => $email->getAddress(), 'type' => 'to'];
            })->all(),
            'subject' => $email->getSubject(),
            'text' => $email->getTextBody(),
        ]]);
    }

    /**
     * 获取传输的字符串表示
     */
    public function __toString(): string
    {
        return 'mailchimp';
    }
}
```

定义好自定义传输后，你可以通过 `Mail` facade 的 `extend` 方法注册它。
通常，这应在应用的 `AppServiceProvider` 的 `boot` 方法中完成。
`$config` 参数会传递给提供给 `extend` 方法的闭包，包含在应用 `config/mail.php` 配置文件中定义的邮件配置数组：

```php
use App\Mail\MailchimpTransport;
use Illuminate\Support\Facades\Mail;

/**
 * 启动应用服务
 */
public function boot(): void
{
    Mail::extend('mailchimp', function (array $config = []) {
        return new MailchimpTransport(/* ... */);
    });
}
```



一旦你的自定义传输被定义并注册，你就可以在应用的 `config/mail.php` 配置文件中创建一个邮件器定义，使用这个新传输：

```php
'mailchimp' => [
    'transport' => 'mailchimp',
    // ...
],
```

### 额外的 Symfony 传输（Additional Symfony Transports）

Laravel 支持一些已有的 Symfony 邮件传输，例如 Mailgun 和 Postmark。
不过，你也可以扩展 Laravel，支持其他由 Symfony 维护的传输。
方法是通过 Composer 安装所需的 Symfony 邮件器，并在 Laravel 中注册传输。例如，你可以安装并注册 “Brevo”（前身为 Sendinblue）Symfony 邮件器：

```shell
composer require symfony/brevo-mailer symfony/http-client
```

安装 Brevo 邮件器包后，可以在应用的 `services` 配置文件中添加 Brevo API 凭证：

```php
'brevo' => [
    'key' => 'your-api-key',
],
```

接下来，你可以使用 `Mail` facade 的 `extend` 方法将传输注册到 Laravel。
通常，这应该在服务提供者的 `boot` 方法中完成：

```php
use Illuminate\Support\Facades\Mail;
use Symfony\Component\Mailer\Bridge\Brevo\Transport\BrevoTransportFactory;
use Symfony\Component\Mailer\Transport\Dsn;

/**
 * 启动应用服务
 */
public function boot(): void
{
    Mail::extend('brevo', function () {
        return (new BrevoTransportFactory)->create(
            new Dsn(
                'brevo+api',
                'default',
                config('services.brevo.key')
            )
        );
    });
}
```

注册好传输后，你可以在 `config/mail.php` 配置文件中创建一个邮件器定义，使用这个新传输：

```php
'brevo' => [
    'transport' => 'brevo',
    // ...
],
```
