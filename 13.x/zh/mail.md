# 邮件

- [简介](#introduction)
    - [配置](#configuration)
    - [驱动前提条件](#driver-prerequisites)
    - [故障转移配置](#failover-configuration)
    - [轮询配置](#round-robin-configuration)
- [生成邮件类](#generating-mailables)
- [编写邮件类](#writing-mailables)
    - [配置发件人](#configuring-the-sender)
    - [配置视图](#configuring-the-view)
    - [视图数据](#view-data)
    - [附件](#attachments)
    - [内联附件](#inline-attachments)
    - [可附加对象](#attachable-objects)
    - [邮件头](#headers)
    - [标签和元数据](#tags-and-metadata)
    - [自定义 Symfony 消息](#customizing-the-symfony-message)
- [Markdown 邮件类](#markdown-mailables)
    - [生成 Markdown 邮件类](#generating-markdown-mailables)
    - [编写 Markdown 邮件](#writing-markdown-messages)
    - [自定义组件](#customizing-the-components)
- [发送邮件](#sending-mail)
    - [邮件队列](#queueing-mail)
- [渲染邮件](#rendering-mailables)
    - [在浏览器中预览邮件](#previewing-mailables-in-the-browser)
- [本地化邮件](#localizing-mailables)
- [测试](#testing-mailables)
    - [测试邮件内容](#testing-mailable-content)
    - [测试邮件发送](#testing-mailable-sending)
- [邮件与本地开发](#mail-and-local-development)
- [事件](#events)
- [自定义传输方式](#custom-transports)
    - [其他 Symfony 传输方式](#additional-symfony-transports)

<a name="introduction"></a>
## 简介

发送邮件并不复杂。Laravel 提供了简洁易用的邮件 API，由流行的 [Symfony Mailer](https://symfony.com/doc/current/mailer.html) 组件提供支持。Laravel 和 Symfony Mailer 提供了通过 SMTP、Cloudflare、Mailgun、Postmark、Resend、Amazon SES 和 `sendmail` 发送邮件的驱动，让你能够快速使用自己选择的本地或云服务发送邮件。

<a name="configuration"></a>
### 配置

Laravel 的邮件服务可以通过应用的 `config/mail.php` 配置文件进行配置。该文件中的每个邮件发送器都可以拥有独立的配置，甚至使用不同的「传输方式」，让应用能够通过不同的邮件服务发送特定邮件。例如，应用可以使用 Postmark 发送事务性邮件，同时使用 Amazon SES 发送批量邮件。

在 `mail` 配置文件中，你会找到一个 `mailers` 配置数组。该数组包含 Laravel 支持的各主要邮件驱动 / 传输方式的示例配置，而 `default` 配置值决定了应用发送邮件时默认使用的邮件发送器。

<a name="driver-prerequisites"></a>
### 驱动 / 传输前提条件

基于 API 的驱动（如 Mailgun、Postmark 和 Resend）通常比通过 SMTP 服务器发送邮件更简单、更快。只要条件允许，我们建议使用这些驱动之一。

<a name="cloudflare-driver"></a>
#### Cloudflare 驱动

要使用 Cloudflare 驱动，请通过 Composer 安装 Symfony 的 HTTP Client：

```shell
composer require symfony/http-client
```

接下来，需要在应用的 `config/mail.php` 配置文件中进行两处修改。首先，将默认邮件发送器设置为 `cloudflare`：

```php
'default' => env('MAIL_MAILER', 'cloudflare'),
```

其次，将以下配置数组添加到 `mailers` 数组中：

```php
'cloudflare' => [
    'transport' => 'cloudflare',
],
```

配置好应用的默认邮件发送器后，将以下选项添加到 `config/services.php` 配置文件中：

```php
'cloudflare' => [
    'account_id' => env('CLOUDFLARE_ACCOUNT_ID'),
    'key' => env('CLOUDFLARE_KEY'),
],
```

<a name="mailgun-driver"></a>
#### Mailgun 驱动

要使用 Mailgun 驱动，请通过 Composer 安装 Symfony 的 Mailgun Mailer 传输包：

```shell
composer require symfony/mailgun-mailer symfony/http-client
```

接下来，需要在应用的 `config/mail.php` 配置文件中进行两处修改。首先，将默认邮件发送器设置为 `mailgun`：

```php
'default' => env('MAIL_MAILER', 'mailgun'),
```

其次，将以下配置数组添加到 `mailers` 数组中：

```php
'mailgun' => [
    'transport' => 'mailgun',
    // 'client' => [
    //     'timeout' => 5,
    // ],
],
```

配置好应用的默认邮件发送器后，将以下选项添加到 `config/services.php` 配置文件中：

```php
'mailgun' => [
    'domain' => env('MAILGUN_DOMAIN'),
    'secret' => env('MAILGUN_SECRET'),
    'endpoint' => env('MAILGUN_ENDPOINT', 'api.mailgun.net'),
    'scheme' => 'https',
],
```

如果你使用的不是美国 [Mailgun 区域](https://documentation.mailgun.com/docs/mailgun/api-reference/api-overview#mailgun-regions)，可以在 `services` 配置文件中定义对应区域的端点：

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

要使用 [Postmark](https://postmarkapp.com/) 驱动，请通过 Composer 安装 Symfony 的 Postmark Mailer 传输包：

```shell
composer require symfony/postmark-mailer symfony/http-client
```

接下来，将应用的 `config/mail.php` 配置文件中的 `default` 选项设置为 `postmark`。配置好默认邮件发送器后，请确保 `config/services.php` 配置文件包含以下选项：

```php
'postmark' => [
    'key' => env('POSTMARK_API_KEY'),
],
```

如果你想指定某个邮件发送器使用的 Postmark 消息流，可以在该发送器的配置数组中添加 `message_stream_id` 配置选项。该数组位于应用的 `config/mail.php` 配置文件中：

```php
'postmark' => [
    'transport' => 'postmark',
    'message_stream_id' => env('POSTMARK_MESSAGE_STREAM_ID'),
    // 'client' => [
    //     'timeout' => 5,
    // ],
],
```

这样，你也可以设置多个使用不同消息流的 Postmark 邮件发送器。

<a name="resend-driver"></a>
#### Resend 驱动

要使用 [Resend](https://resend.com/) 驱动，请通过 Composer 安装 Resend 的 PHP SDK：

```shell
composer require resend/resend-php
```

接下来，将应用的 `config/mail.php` 配置文件中的 `default` 选项设置为 `resend`。配置好默认邮件发送器后，请确保 `config/services.php` 配置文件包含以下选项：

```php
'resend' => [
    'key' => env('RESEND_API_KEY'),
],
```

<a name="ses-driver"></a>
#### SES 驱动

要使用 Amazon SES 驱动，必须先安装 Amazon AWS SDK for PHP。你可以通过 Composer 包管理器安装这个库：

```shell
composer require aws/aws-sdk-php
```

接下来，将 `config/mail.php` 配置文件中的 `default` 选项设置为 `ses`，并确保 `config/services.php` 配置文件包含以下选项：

```php
'ses' => [
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
],
```

要通过会话令牌使用 AWS [临时凭证](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_use-resources.html)，可以在应用的 SES 配置中添加 `token` 键：

```php
'ses' => [
    'key' => env('AWS_ACCESS_KEY_ID'),
    'secret' => env('AWS_SECRET_ACCESS_KEY'),
    'region' => env('AWS_DEFAULT_REGION', 'us-east-1'),
    'token' => env('AWS_SESSION_TOKEN'),
],
```

要使用 SES 的 [订阅管理功能](https://docs.aws.amazon.com/ses/latest/dg/sending-email-subscription-management.html)，可以在邮件的 [headers](#headers) 方法返回的数组中包含 `X-Ses-List-Management-Options` 邮件头：

```php
/**
 * 获取邮件头。
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

要通过 SES [租户](https://docs.aws.amazon.com/ses/latest/dg/tenants.html) 发送邮件，可以在 `headers` 方法中返回 `X-Ses-Tenant-Name` 邮件头。发送邮件时，Laravel 会将该邮件头的值作为 `TenantName` 选项传递给 SES：

```php
public function headers(): Headers
{
    return new Headers(
        text: [
            'X-Ses-Tenant-Name' => 'tenant-id',
        ],
    );
}
```

如果你想定义 Laravel 发送邮件时传递给 AWS SDK 的 `SendEmail` 方法的 [额外选项](https://docs.aws.amazon.com/aws-sdk-php/v3/api/api-sesv2-2019-09-27.html#sendemail)，可以在 `ses` 配置中定义 `options` 数组：

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

<a name="failover-configuration"></a>
### 故障转移配置

有时，为应用配置的外部邮件服务可能会发生故障。在这种情况下，定义一个或多个备用邮件发送配置就很有用，可以在主要发送驱动不可用时启用它们。

为此，请在应用的 `mail` 配置文件中定义一个使用 `failover` 传输方式的邮件发送器。其配置数组应包含一个 `mailers` 数组，按顺序列出发送邮件时应尝试的已配置发送器：

```php
'mailers' => [
    'failover' => [
        'transport' => 'failover',
        'mailers' => [
            'postmark',
            'mailgun',
            'sendmail',
        ],
        'retry_after' => 60,
    ],

    // ...
],
```

配置好使用 `failover` 传输方式的邮件发送器后，需要在应用的 `.env` 文件中将其设置为默认邮件发送器，才能启用故障转移功能：

```ini
MAIL_MAILER=failover
```

<a name="round-robin-configuration"></a>
### 轮询配置

`roundrobin` 传输方式允许将邮件发送工作负载分配到多个发送器上。首先，在应用的 `mail` 配置文件中定义一个使用 `roundrobin` 传输方式的邮件发送器。其配置数组应包含一个 `mailers` 数组，列出用于发送邮件的已配置发送器：

```php
'mailers' => [
    'roundrobin' => [
        'transport' => 'roundrobin',
        'mailers' => [
            'ses',
            'postmark',
        ],
        'retry_after' => 60,
    ],

    // ...
],
```

定义好轮询邮件发送器后，请在应用的 `mail` 配置文件中将 `default` 配置键设置为该发送器的名称，以便将其作为应用的默认邮件发送器：

```php
'default' => env('MAIL_MAILER', 'roundrobin'),
```

轮询传输会从已配置的邮件发送器列表中随机选择一个，然后在后续每封邮件中切换到下一个可用发送器。与帮助实现 *[高可用性](https://en.wikipedia.org/wiki/High_availability)* 的 `failover` 传输不同，`roundrobin` 传输提供的是 *[负载均衡](https://en.wikipedia.org/wiki/Load_balancing_(computing))*。

<a name="generating-mailables"></a>
## 生成邮件类

构建 Laravel 应用时，应用发送的每种邮件都由一个「mailable」邮件类表示。这些类存储在 `app/Mail` 目录中。如果应用中没有这个目录，不必担心：使用 `make:mail` Artisan 命令创建第一个邮件类时，系统会自动生成它：

```shell
php artisan make:mail OrderShipped
```

<a name="writing-mailables"></a>
## 编写邮件类

生成邮件类后，打开它来查看其内容。邮件类的配置通过多个方法完成，包括 `envelope`、`content` 和 `attachments` 方法。

`envelope` 方法返回一个 `Illuminate\Mail\Mailables\Envelope` 对象，用于定义邮件主题，有时也定义收件人。`content` 方法返回一个 `Illuminate\Mail\Mailables\Content` 对象，用于定义生成邮件内容所使用的 [Blade 模板](/docs/{{version}}/blade)。

<a name="configuring-the-sender"></a>
### 配置发件人

<a name="using-the-envelope"></a>
#### 使用信封配置

首先，来看看如何配置邮件的发件人，也就是邮件「来自」谁。有两种方式可以配置发件人。第一种是在邮件的信封配置中指定「from」地址：

```php
use Illuminate\Mail\Mailables\Address;
use Illuminate\Mail\Mailables\Envelope;

/**
 * 获取邮件信封。
 */
public function envelope(): Envelope
{
    return new Envelope(
        from: new Address('jeffrey@example.com', 'Jeffrey Way'),
        subject: 'Order Shipped',
    );
}
```

如果需要，也可以指定 `replyTo` 地址：

```php
return new Envelope(
    from: new Address('jeffrey@example.com', 'Jeffrey Way'),
    replyTo: [
        new Address('taylor@example.com', 'Taylor Otwell'),
    ],
    subject: 'Order Shipped',
);
```

<a name="using-a-global-from-address"></a>
#### 使用全局 `from` 地址

如果应用的所有邮件都使用同一个「from」地址，为每个生成的邮件类添加该地址会很繁琐。你可以改为在 `config/mail.php` 配置文件中指定全局「from」地址。如果邮件类中没有指定其他「from」地址，就会使用这个地址：

```php
'from' => [
    'address' => env('MAIL_FROM_ADDRESS', 'hello@example.com'),
    'name' => env('MAIL_FROM_NAME', 'Example'),
],
```

此外，也可以在 `config/mail.php` 配置文件中定义全局「reply_to」地址：

```php
'reply_to' => [
    'address' => 'example@example.com',
    'name' => 'App Name',
],
```

<a name="configuring-the-view"></a>
### 配置视图

在邮件类的 `content` 方法中，你可以定义 `view`，即渲染邮件内容时使用的模板。由于每封邮件通常都使用 [Blade 模板](/docs/{{version}}/blade) 渲染内容，你可以在构建邮件 HTML 时充分利用 Blade 模板引擎的全部功能和便利性：

```php
/**
 * 获取邮件内容定义。
 */
public function content(): Content
{
    return new Content(
        view: 'mail.orders.shipped',
    );
}
```

> [!NOTE]
> 你可以创建一个 `resources/views/mail` 目录来存放所有邮件模板；当然，也可以将它们放在 `resources/views` 目录中的任何位置。

<a name="plain-text-emails"></a>
#### 纯文本邮件

如果你想定义邮件的纯文本版本，可以在创建邮件的 `Content` 定义时指定纯文本模板。与 `view` 参数类似，`text` 参数应为用于渲染邮件内容的模板名称。你可以同时定义邮件的 HTML 和纯文本版本：

```php
/**
 * 获取邮件内容定义。
 */
public function content(): Content
{
    return new Content(
        view: 'mail.orders.shipped',
        text: 'mail.orders.shipped-text'
    );
}
```

为了更清晰，也可以使用 `html` 参数作为 `view` 参数的别名：

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

通常，你需要向视图传递一些数据，以便在渲染邮件 HTML 时使用。有两种方式可以让视图获取数据。第一种是利用邮件类上定义的公共属性，它们会自动提供给视图。例如，你可以将数据传入邮件类的构造函数，并将其赋给类的公共属性：

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
     * 创建新的邮件实例。
     */
    public function __construct(
        public Order $order,
    ) {}

    /**
     * 获取邮件内容定义。
     */
    public function content(): Content
    {
        return new Content(
            view: 'mail.orders.shipped',
        );
    }
}
```

数据赋给公共属性后，就会自动提供给视图，你可以像访问 Blade 模板中的其他数据一样访问它：

```blade
<div>
    Price: {{ $order->price }}
</div>
```

<a name="via-the-with-parameter"></a>
#### 通过 `with` 参数传递：

如果你想在将邮件数据传入模板之前调整其格式，可以通过 `Content` 定义的 `with` 参数手动将数据传给视图。通常，你仍会通过邮件类的构造函数传入数据；不过，应将数据赋给 `protected` 或 `private` 属性，避免自动提供给模板：

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
     * 创建新的邮件实例。
     */
    public function __construct(
        protected Order $order,
    ) {}

    /**
     * 获取邮件内容定义。
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

通过 `with` 参数传入的数据会自动提供给视图，你可以像访问 Blade 模板中的其他数据一样访问它：

```blade
<div>
    Price: {{ $orderPrice }}
</div>
```

<a name="attachments"></a>
### 附件

要为邮件添加附件，请将附件添加到邮件的 `attachments` 方法返回的数组中。首先，可以将文件路径传递给 `Attachment` 类的 `fromPath` 方法来添加附件：

```php
use Illuminate\Mail\Mailables\Attachment;

/**
 * 获取邮件附件。
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

为邮件添加附件时，也可以使用 `as` 和 `withMime` 方法指定附件的显示名称和 / 或 MIME 类型：

```php
/**
 * 获取邮件附件。
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

如果文件存储在某个 [文件系统磁盘](/docs/{{version}}/filesystem) 上，可以使用 `fromStorage` 附件方法将其附加到邮件中：

```php
/**
 * 获取邮件附件。
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

当然，也可以指定附件的名称和 MIME 类型：

```php
/**
 * 获取邮件附件。
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

如果需要指定非默认的存储磁盘，可以使用 `fromStorageDisk` 方法：

```php
/**
 * 获取邮件附件。
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

`fromData` 附件方法可以将原始字节字符串作为附件。例如，当你在内存中生成了 PDF，希望将其附加到邮件而不写入磁盘时，就可以使用这个方法。`fromData` 方法接受一个返回原始数据字节的闭包，以及要分配给附件的名称：

```php
/**
 * 获取邮件附件。
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

<a name="inline-attachments"></a>
### 内联附件

将内联图片嵌入邮件通常比较麻烦，但 Laravel 提供了方便的方法。要嵌入内联图片，请在邮件模板中对 `$message` 变量调用 `embed` 方法。Laravel 会自动将 `$message` 变量提供给所有邮件模板，因此无需手动传入：

```blade
<body>
    Here is an image:

    <img src="{{ $message->embed($pathToImage) }}">
</body>
```

> [!WARNING]
> `$message` 变量在纯文本邮件模板中不可用，因为纯文本邮件不使用内联附件。

<a name="embedding-raw-data-attachments"></a>
#### 嵌入原始数据附件

如果你已有一段原始图片数据字符串，想将其嵌入邮件模板，可以对 `$message` 变量调用 `embedData` 方法。调用该方法时，需要提供分配给嵌入图片的文件名：

```blade
<body>
    Here is an image from raw data:

    <img src="{{ $message->embedData($data, 'example-image.jpg') }}">
</body>
```

<a name="attachable-objects"></a>
### 可附加对象

通过简单的字符串路径将文件附加到邮件通常就已足够，但在很多情况下，应用中可作为附件的实体是由类表示的。例如，要将一张照片附加到邮件中，应用可能也有一个表示这张照片的 `Photo` 模型。此时，如果能直接将 `Photo` 模型传给 `attach` 方法，会不会更方便？可附加对象就能实现这一点。

首先，让可附加到邮件的对象实现 `Illuminate\Contracts\Mail\Attachable` 接口。该接口要求类定义一个 `toMailAttachment` 方法，并返回 `Illuminate\Mail\Attachment` 实例：

```php
<?php

namespace App\Models;

use Illuminate\Contracts\Mail\Attachable;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Mail\Attachment;

class Photo extends Model implements Attachable
{
    /**
     * 获取模型的附件表示。
     */
    public function toMailAttachment(): Attachment
    {
        return Attachment::fromPath('/path/to/file');
    }
}
```

定义好可附加对象后，可以在构建邮件时从 `attachments` 方法中返回该对象的实例：

```php
/**
 * 获取邮件附件。
 *
 * @return array<int, \Illuminate\Mail\Mailables\Attachment>
 */
public function attachments(): array
{
    return [$this->photo];
}
```

当然，附件数据也可能存储在 Amazon S3 等远程文件存储服务中。因此，Laravel 也允许你根据存储在应用某个 [文件系统磁盘](/docs/{{version}}/filesystem) 上的数据生成附件实例：

```php
// 从默认磁盘上的文件创建附件……
return Attachment::fromStorage($this->path);

// 从指定磁盘上的文件创建附件……
return Attachment::fromStorageDisk('backblaze', $this->path);
```

此外，也可以使用内存中的数据创建附件实例。为此，请向 `fromData` 方法传入一个闭包，该闭包应返回表示附件的原始数据：

```php
return Attachment::fromData(fn () => $this->content, 'Photo Name');
```

Laravel 还提供了其他方法来自定义附件。例如，可以使用 `as` 和 `withMime` 方法自定义文件名和 MIME 类型：

```php
return Attachment::fromPath('/path/to/file')
    ->as('Photo Name')
    ->withMime('image/jpeg');
```

<a name="headers"></a>
### 邮件头

有时，你需要为要发送的邮件添加额外的邮件头。例如，设置自定义的 `Message-Id` 或其他任意文本邮件头。

为此，请在邮件类上定义 `headers` 方法。该方法应返回一个 `Illuminate\Mail\Mailables\Headers` 实例。这个类接受 `messageId`、`references` 和 `text` 参数。当然，你只需提供该邮件所需的参数：

```php
use Illuminate\Mail\Mailables\Headers;

/**
 * 获取邮件头。
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

<a name="tags-and-metadata"></a>
### 标签和元数据

一些第三方邮件服务商（如 Mailgun 和 Postmark）支持邮件「标签」和「元数据」，可用于对应用发送的邮件进行分组和追踪。你可以通过 `Envelope` 定义为邮件添加标签和元数据：

```php
use Illuminate\Mail\Mailables\Envelope;

/**
 * 获取邮件信封。
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

如果应用使用 Mailgun 驱动，可以查阅 Mailgun 文档，了解 [标签](https://documentation.mailgun.com/docs/mailgun/user-manual/tracking-messages/#tags) 和 [元数据](https://documentation.mailgun.com/docs/mailgun/user-manual/sending-messages/#attaching-metadata-to-messages) 的更多信息。同样，也可以查阅 Postmark 文档，了解其对 [标签](https://postmarkapp.com/blog/tags-support-for-smtp) 和 [元数据](https://postmarkapp.com/support/article/1125-custom-metadata-faq) 的支持。

如果应用使用 Amazon SES 发送邮件，应使用 `metadata` 方法为邮件添加 [SES「标签」](https://docs.aws.amazon.com/ses/latest/APIReference/API_MessageTag.html)。

<a name="customizing-the-symfony-message"></a>
### 自定义 Symfony 消息

Laravel 的邮件功能由 Symfony Mailer 提供支持。Laravel 允许注册自定义回调，在发送邮件前调用，并将 Symfony 消息实例传给回调。这让你能够在发送前对邮件进行深度定制。为此，请在 `Envelope` 定义中设置 `using` 参数：

```php
use Illuminate\Mail\Mailables\Envelope;
use Symfony\Component\Mime\Email;

/**
 * 获取邮件信封。
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

<a name="markdown-mailables"></a>
## Markdown 邮件类

Markdown 邮件类允许你在邮件中使用 [邮件通知](/docs/{{version}}/notifications#mail-notifications) 预先构建的模板和组件。由于邮件使用 Markdown 编写，Laravel 能够将其渲染成美观、响应式的 HTML 模板，同时自动生成对应的纯文本版本。

<a name="generating-markdown-mailables"></a>
### 生成 Markdown 邮件类

要生成带有对应 Markdown 模板的邮件类，可以使用 `make:mail` Artisan 命令的 `--markdown` 选项：

```shell
php artisan make:mail OrderShipped --markdown=mail.orders.shipped
```

然后，在邮件类的 `content` 方法中配置 `Content` 定义时，请使用 `markdown` 参数而不是 `view` 参数：

```php
use Illuminate\Mail\Mailables\Content;

/**
 * 获取邮件内容定义。
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

<a name="writing-markdown-messages"></a>
### 编写 Markdown 邮件

Markdown 邮件类结合了 Blade 组件和 Markdown 语法，让你可以轻松构建邮件，同时使用 Laravel 预先构建的邮件 UI 组件：

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

> [!NOTE]
> 编写 Markdown 邮件时，不要使用多余的缩进。根据 Markdown 标准，解析器会将缩进内容渲染为代码块。

<a name="button-component"></a>
#### 按钮组件

按钮组件会渲染一个居中的按钮链接。该组件接受两个参数：`url` 和可选的 `color`。支持的颜色有 `primary`、`success` 和 `error`。你可以在邮件中添加任意数量的按钮组件：

```blade
<x-mail::button :url="$url" color="success">
View Order
</x-mail::button>
```

<a name="panel-component"></a>
#### 面板组件

面板组件将指定文本块渲染在一个面板中，其背景颜色与邮件的其余部分略有不同，以便突出显示这段文本：

```blade
<x-mail::panel>
This is the panel content.
</x-mail::panel>
```

<a name="table-component"></a>
#### 表格组件

表格组件可以将 Markdown 表格转换为 HTML 表格。该组件接受 Markdown 表格作为内容，并支持使用默认的 Markdown 表格对齐语法设置列对齐方式：

```blade
<x-mail::table>
| Laravel       | Table         | Example       |
| ------------- | :-----------: | ------------: |
| Col 2 is      | Centered      | $10           |
| Col 3 is      | Right-Aligned | $20           |
</x-mail::table>
```

<a name="customizing-the-components"></a>
### 自定义组件

你可以将所有 Markdown 邮件组件导出到自己的应用中进行自定义。要导出组件，请使用 `vendor:publish` Artisan 命令发布 `laravel-mail` 资源标签：

```shell
php artisan vendor:publish --tag=laravel-mail
```

该命令会将 Markdown 邮件组件发布到 `resources/views/vendor/mail` 目录。`mail` 目录中包含 `html` 和 `text` 两个目录，分别存放每个可用组件的 HTML 和纯文本版本。你可以自由地自定义这些组件。

<a name="customizing-the-css"></a>
#### 自定义 CSS

导出组件后，`resources/views/vendor/mail/html/themes` 目录中会包含一个 `default.css` 文件。你可以修改该文件中的 CSS，这些样式会自动转换为 Markdown 邮件 HTML 版本中的内联 CSS 样式。

如果你想为 Laravel 的 Markdown 组件构建全新的主题，可以在 `html/themes` 目录中放置一个 CSS 文件。命名并保存文件后，更新应用的 `config/mail.php` 配置文件中的 `theme` 选项，使其与新主题名称一致。

要为单个邮件类自定义主题，可以将该类的 `$theme` 属性设置为发送邮件时使用的主题名称。

<a name="sending-mail"></a>
## 发送邮件

要发送邮件，请使用 `Mail` [facade](/docs/{{version}}/facades) 的 `to` 方法。该方法接受邮箱地址、用户实例或用户集合。如果传入对象或对象集合，邮件发送器会自动使用其 `email` 和 `name` 属性来确定收件人，因此请确保对象具有这些属性。指定收件人后，可以将邮件类的实例传给 `send` 方法：

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
     * 为指定订单发货。
     */
    public function store(Request $request): RedirectResponse
    {
        $order = Order::findOrFail($request->order_id);

        // 处理订单发货……

        Mail::to($request->user())->send(new OrderShipped($order));

        return redirect('/orders');
    }
}
```

发送邮件时，不仅可以指定「to」收件人，也可以通过链式调用相应方法设置「to」、「cc」和「bcc」收件人：

```php
Mail::to($request->user())
    ->cc($moreUsers)
    ->bcc($evenMoreUsers)
    ->send(new OrderShipped($order));
```

<a name="looping-over-recipients"></a>
#### 遍历收件人

有时，你需要遍历收件人 / 邮箱地址数组来向一组收件人发送邮件。但由于 `to` 方法会将邮箱地址追加到邮件实例的收件人列表中，每次循环都会向之前的所有收件人再次发送邮件。因此，应始终为每个收件人重新创建邮件实例：

```php
foreach (['taylor@example.com', 'dries@example.com'] as $recipient) {
    Mail::to($recipient)->send(new OrderShipped($order));
}
```

<a name="sending-mail-via-a-specific-mailer"></a>
#### 使用特定邮件发送器发送邮件

默认情况下，Laravel 会使用应用的 `mail` 配置文件中设为 `default` 的邮件发送器发送邮件。不过，你也可以使用 `mailer` 方法指定某个邮件发送器配置：

```php
Mail::mailer('postmark')
    ->to($request->user())
    ->send(new OrderShipped($order));
```

<a name="queueing-mail"></a>
### 邮件队列

<a name="queueing-a-mail-message"></a>
#### 将邮件加入队列

由于发送邮件可能拖慢应用的响应，许多开发者会选择将邮件加入队列，在后台发送。Laravel 内置的 [统一队列 API](/docs/{{version}}/queues) 让这变得很简单。要将邮件加入队列，请在指定收件人后调用 `Mail` facade 的 `queue` 方法：

```php
Mail::to($request->user())
    ->cc($moreUsers)
    ->bcc($evenMoreUsers)
    ->queue(new OrderShipped($order));
```

该方法会自动将任务推送到队列中，以便在后台发送邮件。使用此功能之前，需要先 [配置队列](/docs/{{version}}/queues)。

<a name="delayed-message-queueing"></a>
#### 延迟发送队列邮件

如果你希望延迟发送队列中的邮件，可以使用 `later` 方法。该方法的第一个参数接受一个 `DateTime` 实例，用于指定邮件发送时间：

```php
Mail::to($request->user())
    ->cc($moreUsers)
    ->bcc($evenMoreUsers)
    ->later(now()->plus(minutes: 10), new OrderShipped($order));
```

<a name="pushing-to-specific-queues"></a>
#### 推送到特定队列

由于使用 `make:mail` 命令生成的所有邮件类都使用了 `Illuminate\Bus\Queueable` trait，你可以在任何邮件类实例上调用 `onQueue` 和 `onConnection` 方法，以指定邮件的连接和队列名称：

```php
$message = (new OrderShipped($order))
    ->onConnection('sqs')
    ->onQueue('emails');

Mail::to($request->user())
    ->cc($moreUsers)
    ->bcc($evenMoreUsers)
    ->queue($message);
```

也可以在邮件类上使用 `Connection` 和 `Queue` 属性来指定连接和队列：

```php
use Illuminate\Queue\Attributes\Connection;
use Illuminate\Queue\Attributes\Queue;

#[Connection('sqs')]
#[Queue('emails')]
class OrderShipped extends Mailable
{
    // ...
}
```

<a name="queueing-by-default"></a>
#### 默认使用队列

如果希望某些邮件类始终加入队列，可以让它们实现 `ShouldQueue` 契约。这样，即使调用 `send` 方法发送邮件，邮件也会因为实现了该契约而被加入队列：

```php
use Illuminate\Contracts\Queue\ShouldQueue;

class OrderShipped extends Mailable implements ShouldQueue
{
    // ...
}
```

<a name="queued-mailables-and-database-transactions"></a>
#### 队列邮件与数据库事务

在数据库事务中派发队列邮件时，队列可能会在事务提交前就处理邮件。此时，在事务中对模型或数据库记录的更新可能尚未反映到数据库中。此外，事务中创建的模型或记录可能还不存在于数据库中。如果邮件依赖这些模型，处理发送邮件的队列任务时就可能发生意外错误。

如果队列连接的 `after_commit` 配置选项设为 `false`，你仍可以在发送邮件时调用 `afterCommit` 方法，指定某封队列邮件应在所有尚未提交的数据库事务提交后才派发：

```php
Mail::to($request->user())->send(
    (new OrderShipped($order))->afterCommit()
);
```

也可以在邮件类的构造函数中调用 `afterCommit` 方法：

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
     * 创建新的邮件实例。
     */
    public function __construct()
    {
        $this->afterCommit();
    }
}
```

> [!NOTE]
> 要了解如何解决这些问题，请参阅 [队列任务与数据库事务](/docs/{{version}}/queues#jobs-and-database-transactions) 文档。

<a name="queued-email-failures"></a>
#### 队列邮件发送失败

当队列邮件发送失败时，如果邮件类定义了 `failed` 方法，就会调用该方法。导致邮件发送失败的 `Throwable` 实例会传递给 `failed` 方法：

```php
<?php

namespace App\Mail;

use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Queue\SerializesModels;
use Throwable;

class OrderDelayed extends Mailable implements ShouldQueue
{
    use SerializesModels;

    /**
     * 处理队列邮件发送失败。
     */
    public function failed(Throwable $exception): void
    {
        // ...
    }
}
```

<a name="rendering-mailables"></a>
## 渲染邮件

有时，你可能希望获取邮件的 HTML 内容而不实际发送。为此，可以调用邮件实例的 `render` 方法。该方法会将渲染后的 HTML 内容作为字符串返回：

```php
use App\Mail\InvoicePaid;
use App\Models\Invoice;

$invoice = Invoice::find(1);

return (new InvoicePaid($invoice))->render();
```

<a name="previewing-mailables-in-the-browser"></a>
### 在浏览器中预览邮件

设计邮件模板时，像普通 Blade 模板一样在浏览器中快速预览渲染后的邮件会很方便。因此，Laravel 允许你直接从路由闭包或控制器中返回任何邮件实例。返回的邮件会被渲染并显示在浏览器中，让你无需发送到真实邮箱就能快速预览其设计：

```php
Route::get('/mailable', function () {
    $invoice = App\Models\Invoice::find(1);

    return new App\Mail\InvoicePaid($invoice);
});
```

<a name="localizing-mailables"></a>
## 本地化邮件

Laravel 允许使用不同于请求当前语言环境的语言发送邮件，即使邮件被加入队列，也会记住该语言环境。

为此，`Mail` facade 提供了 `locale` 方法来设置所需的语言。应用会在渲染邮件模板时切换到该语言环境，渲染完成后再恢复之前的语言环境：

```php
Mail::to($request->user())->locale('es')->send(
    new OrderShipped($order)
);
```

<a name="user-preferred-locales"></a>
#### 用户首选语言

有时，应用会存储每个用户的首选语言。通过在一个或多个模型上实现 `HasLocalePreference` 契约，你可以让 Laravel 在发送邮件时使用所存储的语言环境：

```php
use Illuminate\Contracts\Translation\HasLocalePreference;

class User extends Model implements HasLocalePreference
{
    /**
     * 获取用户的首选语言。
     */
    public function preferredLocale(): string
    {
        return $this->locale;
    }
}
```

实现该接口后，Laravel 会在向该模型发送邮件和通知时自动使用其首选语言。因此，使用该接口时不必再调用 `locale` 方法：

```php
Mail::to($request->user())->send(new OrderShipped($order));
```

<a name="testing-mailables"></a>
## 测试

<a name="testing-mailable-content"></a>
### 测试邮件内容

Laravel 提供了多种方法来检查邮件的结构。此外，还提供了几个便捷的方法，用于测试邮件是否包含预期内容：

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
    $mailable->assertDontSeeInHtml('Invoice Not Paid');
    $mailable->assertSeeInOrderInHtml(['Invoice Paid', 'Thanks']);

    $mailable->assertSeeInText($user->email);
    $mailable->assertDontSeeInText('Invoice Not Paid');
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
    $mailable->assertDontSeeInHtml('Invoice Not Paid');
    $mailable->assertSeeInOrderInHtml(['Invoice Paid', 'Thanks']);

    $mailable->assertSeeInText($user->email);
    $mailable->assertDontSeeInText('Invoice Not Paid');
    $mailable->assertSeeInOrderInText(['Invoice Paid', 'Thanks']);

    $mailable->assertHasAttachment('/path/to/file');
    $mailable->assertHasAttachment(Attachment::fromPath('/path/to/file'));
    $mailable->assertHasAttachedData($pdfData, 'name.pdf', ['mime' => 'application/pdf']);
    $mailable->assertHasAttachmentFromStorage('/path/to/file', 'name.pdf', ['mime' => 'application/pdf']);
    $mailable->assertHasAttachmentFromStorageDisk('s3', '/path/to/file', 'name.pdf', ['mime' => 'application/pdf']);
}
```

顾名思义，「HTML」断言用于检查邮件的 HTML 版本是否包含指定字符串，而「text」断言用于检查邮件的纯文本版本是否包含指定字符串。

<a name="testing-mailable-sending"></a>
### 测试邮件发送

我们建议将邮件内容测试与断言邮件已「发送」给特定用户的测试分开。通常，邮件内容与你正在测试的代码无关，只需断言代码已指示 Laravel 发送指定邮件即可。

你可以使用 `Mail` facade 的 `fake` 方法阻止邮件实际发送。调用后，可以断言程序已指示向用户发送邮件，甚至检查邮件实例接收到的数据：

```php tab=Pest
<?php

use App\Mail\OrderShipped;
use Illuminate\Support\Facades\Mail;

test('orders can be shipped', function () {
    Mail::fake();

    // 执行订单发货操作……

    // 断言没有邮件被发送……
    Mail::assertNothingSent();

    // 断言指定邮件已发送……
    Mail::assertSent(OrderShipped::class);

    // 断言指定邮件发送了两次……
    Mail::assertSent(OrderShipped::class, 2);

    // 断言指定邮件发送到了某个邮箱地址……
    Mail::assertSent(OrderShipped::class, 'example@laravel.com');

    // 断言指定邮件发送到了多个邮箱地址……
    Mail::assertSent(OrderShipped::class, ['example@laravel.com', '...']);

    // 断言指定邮件未发送……
    Mail::assertNotSent(AnotherMailable::class);

    // 断言指定邮件发送了两次……
    Mail::assertSentTimes(OrderShipped::class, 2);

    // 断言指定邮件恰好发送了一次……
    Mail::assertSentOnce(OrderShipped::class);

    // 断言总共发送了 3 封邮件……
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

        // 执行订单发货操作……

        // 断言没有邮件被发送……
        Mail::assertNothingSent();

        // 断言指定邮件已发送……
        Mail::assertSent(OrderShipped::class);

        // 断言指定邮件发送了两次……
        Mail::assertSent(OrderShipped::class, 2);

        // 断言指定邮件发送到了某个邮箱地址……
        Mail::assertSent(OrderShipped::class, 'example@laravel.com');

        // 断言指定邮件发送到了多个邮箱地址……
        Mail::assertSent(OrderShipped::class, ['example@laravel.com', '...']);

        // 断言指定邮件未发送……
        Mail::assertNotSent(AnotherMailable::class);

        // 断言指定邮件发送了两次……
        Mail::assertSentTimes(OrderShipped::class, 2);

        // 断言指定邮件恰好发送了一次……
        Mail::assertSentOnce(OrderShipped::class);

        // 断言总共发送了 3 封邮件……
        Mail::assertSentCount(3);
    }
}
```

如果将邮件加入队列在后台发送，应使用 `assertQueued` 方法而不是 `assertSent`：

```php
Mail::assertQueued(OrderShipped::class);
Mail::assertQueuedOnce(OrderShipped::class);
Mail::assertNotQueued(OrderShipped::class);
Mail::assertNothingQueued();
Mail::assertQueuedCount(3);
```

还可以使用 `assertOutgoingCount` 方法断言已发送或已加入队列的邮件总数：

```php
Mail::assertOutgoingCount(3);
```

你可以向 `assertSent`、`assertNotSent`、`assertQueued` 或 `assertNotQueued` 方法传入闭包，以检查邮件是否满足指定条件。对于发送成功的断言，只要至少有一封已发送邮件满足该条件，断言就会通过：

```php
Mail::assertSent(function (OrderShipped $mail) use ($order) {
    return $mail->order->id === $order->id;
});
```

调用 `Mail` facade 的断言方法时，传入闭包的邮件实例提供了多种便于检查邮件的方法：

```php
Mail::assertSent(OrderShipped::class, function (OrderShipped $mail) use ($user) {
    return $mail->hasTo($user->email) &&
           $mail->hasCc('...') &&
           $mail->hasBcc('...') &&
           $mail->hasReplyTo('...') &&
           $mail->hasFrom('...') &&
           $mail->hasSubject('...') &&
           $mail->hasMetadata('order_id', $mail->order->id) &&
           $mail->usesMailer('ses');
});
```

邮件实例还提供了几个便于检查附件的方法：

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

你可能已经注意到，用于断言邮件未发送的方法有两个：`assertNotSent` 和 `assertNotQueued`。有时，你希望断言邮件既未发送 **也未** 加入队列。为此，可以使用 `assertNothingOutgoing` 和 `assertNotOutgoing` 方法：

```php
Mail::assertNothingOutgoing();

Mail::assertNotOutgoing(function (OrderShipped $mail) use ($order) {
    return $mail->order->id === $order->id;
});
```

<a name="mail-and-local-development"></a>
## 邮件与本地开发

开发会发送邮件的应用时，你通常不希望将邮件实际发送到真实邮箱。Laravel 提供了几种方式，在本地开发期间「禁用」邮件的实际发送。

<a name="log-driver"></a>
#### 日志驱动

`log` 邮件驱动不会发送邮件，而是将所有邮件内容写入日志文件以便检查。通常，该驱动仅用于本地开发。有关按不同环境配置应用的更多信息，请参阅 [配置文档](/docs/{{version}}/configuration#environment-configuration)。

<a name="mailtrap"></a>
#### HELO / Mailtrap / Mailpit

你也可以使用 [HELO](https://usehelo.com) 或 [Mailtrap](https://mailtrap.io) 等服务，配合 `smtp` 驱动将邮件发送到「模拟」邮箱，从而在真正的邮件客户端中查看。这样做的好处是，可以在 Mailtrap 的邮件查看器中实际检查最终邮件。

如果使用 [Laravel Sail](/docs/{{version}}/sail)，可以通过 [Mailpit](https://github.com/axllent/mailpit) 预览邮件。Sail 运行时，可以通过 `http://localhost:8025` 访问 Mailpit 界面。

<a name="using-a-global-to-address"></a>
#### 使用全局 `to` 地址

最后，可以调用 `Mail` facade 的 `alwaysTo` 方法来指定全局「to」地址。通常，应在应用某个服务提供者的 `boot` 方法中调用它：

```php
use Illuminate\Support\Facades\Mail;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    if ($this->app->environment('local')) {
        Mail::alwaysTo('taylor@example.com');
    }
}
```

使用 `alwaysTo` 方法时，邮件中的所有额外「cc」或「bcc」地址都会被移除。

<a name="events"></a>
## 事件

Laravel 在发送邮件时会派发两个事件：发送之前派发 `MessageSending`，发送之后派发 `MessageSent`。请注意，这些事件在邮件 *实际发送* 时派发，而不是在加入队列时派发。你可以在应用中为这些事件创建 [事件监听器](/docs/{{version}}/events)：

```php
use Illuminate\Mail\Events\MessageSending;
// use Illuminate\Mail\Events\MessageSent;

class LogMessage
{
    /**
     * 处理事件。
     */
    public function handle(MessageSending $event): void
    {
        // ...
    }
}
```

<a name="custom-transports"></a>
## 自定义传输方式

Laravel 内置了多种邮件传输方式。不过，如果想通过 Laravel 默认不支持的服务发送邮件，可以编写自己的传输实现。首先，定义一个继承 `Symfony\Component\Mailer\Transport\AbstractTransport` 的类，然后在其中实现 `doSend` 和 `__toString` 方法：

```php
<?php

namespace App\Mail;

use MailchimpTransactional\ApiClient;
use Symfony\Component\Mailer\SentMessage;
use Symfony\Component\Mailer\Transport\AbstractTransport;
use Symfony\Component\Mime\Address;
use Symfony\Component\Mime\MessageConverter;

class MailchimpTransport extends AbstractTransport
{
    /**
     * 创建新的 Mailchimp 传输实例。
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
     * 获取传输的字符串表示。
     */
    public function __toString(): string
    {
        return 'mailchimp';
    }
}
```

定义好自定义传输后，可以通过 `Mail` facade 的 `extend` 方法注册它。通常，应在应用的 `AppServiceProvider` 的 `boot` 方法中完成注册。传给 `extend` 方法的闭包会接收 `$config` 参数，其中包含应用的 `config/mail.php` 配置文件中为该邮件发送器定义的配置数组：

```php
use App\Mail\MailchimpTransport;
use Illuminate\Support\Facades\Mail;
use MailchimpTransactional\ApiClient;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Mail::extend('mailchimp', function (array $config = []) {
        $client = new ApiClient;

        $client->setApiKey($config['key']);

        return new MailchimpTransport($client);
    });
}
```

定义并注册自定义传输后，可以在应用的 `config/mail.php` 配置文件中定义一个使用该新传输方式的邮件发送器：

```php
'mailchimp' => [
    'transport' => 'mailchimp',
    'key' => env('MAILCHIMP_API_KEY'),
    // ...
],
```

<a name="additional-symfony-transports"></a>
### 其他 Symfony 传输方式

Laravel 支持一些由 Symfony 维护的现有邮件传输方式，例如 Mailgun 和 Postmark。你也可以扩展 Laravel，以支持 Symfony 维护的其他传输方式。只需通过 Composer 安装所需的 Symfony 邮件包，并在 Laravel 中注册传输即可。例如，可以安装并注册「Brevo」（原名「Sendinblue」）Symfony 邮件包：

```shell
composer require symfony/brevo-mailer symfony/http-client
```

安装 Brevo 邮件包后，可以在应用的 `services` 配置文件中添加 Brevo API 凭证：

```php
'brevo' => [
    'key' => env('BREVO_API_KEY'),
],
```

接下来，可以使用 `Mail` facade 的 `extend` 方法将该传输注册到 Laravel。通常，应在服务提供者的 `boot` 方法中完成注册：

```php
use Illuminate\Support\Facades\Mail;
use Symfony\Component\Mailer\Bridge\Brevo\Transport\BrevoTransportFactory;
use Symfony\Component\Mailer\Transport\Dsn;

/**
 * 启动应用服务。
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

注册传输后，可以在应用的 `config/mail.php` 配置文件中定义一个使用该新传输方式的邮件发送器：

```php
'brevo' => [
    'transport' => 'brevo',
    // ...
],
```
