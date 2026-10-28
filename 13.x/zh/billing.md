# Laravel Cashier (Stripe)

- [简介](#introduction)
- [升级 Cashier](#upgrading-cashier)
- [安装](#installation)
- [配置](#configuration)
    - [可计费模型](#billable-model)
    - [API 密钥](#api-keys)
    - [货币配置](#currency-configuration)
    - [税务配置](#tax-configuration)
    - [日志记录](#logging)
    - [使用自定义模型](#using-custom-models)
- [快速入门](#quickstart)
    - [销售产品](#quickstart-selling-products)
    - [销售订阅](#quickstart-selling-subscriptions)
- [客户](#customers)
    - [获取客户](#retrieving-customers)
    - [创建客户](#creating-customers)
    - [更新客户](#updating-customers)
    - [余额](#balances)
    - [税号](#tax-ids)
    - [向 Stripe 同步客户数据](#syncing-customer-data-with-stripe)
    - [账单门户](#billing-portal)
- [支付方式](#payment-methods)
    - [存储支付方式](#storing-payment-methods)
    - [获取支付方式](#retrieving-payment-methods)
    - [检查支付方式是否存在](#payment-method-presence)
    - [更新默认支付方式](#updating-the-default-payment-method)
    - [添加支付方式](#adding-payment-methods)
    - [删除支付方式](#deleting-payment-methods)
- [订阅](#subscriptions)
    - [创建订阅](#creating-subscriptions)
    - [检查订阅状态](#checking-subscription-status)
    - [更改价格](#changing-prices)
    - [订阅数量](#subscription-quantity)
    - [多产品订阅](#subscriptions-with-multiple-products)
    - [多个订阅](#multiple-subscriptions)
    - [按用量计费](#usage-based-billing)
    - [订阅税费](#subscription-taxes)
    - [订阅锚定日期](#subscription-anchor-date)
    - [取消订阅](#cancelling-subscriptions)
    - [恢复订阅](#resuming-subscriptions)
- [订阅试用](#subscription-trials)
    - [预先提供支付方式](#with-payment-method-up-front)
    - [不预先提供支付方式](#without-payment-method-up-front)
    - [延长试用期](#extending-trials)
- [处理 Stripe Webhook](#handling-stripe-webhooks)
    - [定义 Webhook 事件处理器](#defining-webhook-event-handlers)
    - [验证 Webhook 签名](#verifying-webhook-signatures)
- [单次收费](#single-charges)
    - [简单收费](#simple-charge)
    - [开具发票并收费](#charge-with-invoice)
    - [创建支付意向](#creating-payment-intents)
    - [退款](#refunding-charges)
- [发票](#invoices)
    - [获取发票](#retrieving-invoices)
    - [下一张发票](#upcoming-invoices)
    - [预览订阅发票](#previewing-subscription-invoices)
    - [生成发票 PDF](#generating-invoice-pdfs)
- [结账](#checkout)
    - [产品结账](#product-checkouts)
    - [单次收费结账](#single-charge-checkouts)
    - [订阅结账](#subscription-checkouts)
    - [收集税号](#collecting-tax-ids)
    - [游客结账](#guest-checkouts)
- [处理支付失败](#handling-failed-payments)
    - [确认支付](#confirming-payments)
- [强客户认证（SCA）](#strong-customer-authentication)
    - [需要额外确认的支付](#payments-requiring-additional-confirmation)
    - [非会话支付通知](#off-session-payment-notifications)
- [Stripe SDK](#stripe-sdk)
- [测试](#testing)

<a name="introduction"></a>
## 简介

[Laravel Cashier Stripe](https://github.com/laravel/cashier-stripe) 为 [Stripe](https://stripe.com) 的订阅计费服务提供了清晰、流畅的接口，替你处理几乎所有繁琐的订阅计费样板代码。除了基本的订阅管理，Cashier 还支持优惠券、切换订阅、订阅「数量」、取消订阅后的宽限期，甚至能够生成发票 PDF。

<a name="upgrading-cashier"></a>
## 升级 Cashier

升级到新版本的 Cashier 时，请务必仔细阅读 [升级指南](https://github.com/laravel/cashier-stripe/blob/16.x/UPGRADE.md)。

> [!WARNING]
> Cashier 使用你所安装的 `stripe/stripe-php` SDK 版本锁定的 Stripe API 版本。例如，`stripe/stripe-php` 21.x 使用 Stripe API 版本 `2026-08-26.dahlia`。Stripe SDK 的新主版本通常面向新的 Stripe API 版本，因此在将 `stripe/stripe-php` 升级到新主版本之前，应先阅读 [Stripe API 更新日志](https://docs.stripe.com/changelog)。

<a name="installation"></a>
## 安装

首先，使用 Composer 包管理器安装适用于 Stripe 的 Cashier 包：

```shell
composer require laravel/cashier
```

安装完成后，使用 `vendor:publish` Artisan 命令发布 Cashier 的迁移文件：

```shell
php artisan vendor:publish --tag="cashier-migrations"
```

然后，执行数据库迁移：

```shell
php artisan migrate
```

Cashier 的迁移会向 `users` 表添加若干列，还会创建 `subscriptions` 表来存储客户的所有订阅，以及 `subscription_items` 表来存储包含多个价格的订阅项。

如果需要，你也可以使用 `vendor:publish` Artisan 命令发布 Cashier 的配置文件：

```shell
php artisan vendor:publish --tag="cashier-config"
```

最后，为确保 Cashier 正确处理所有 Stripe 事件，请记得 [配置 Cashier 的 Webhook 处理](#handling-stripe-webhooks)。

> [!WARNING]
> Stripe 建议所有用于存储 Stripe 标识符的列都应区分大小写。因此，使用 MySQL 时，请确保 `stripe_id` 列的排序规则设置为 `utf8_bin`。更多信息请参阅 [Stripe 文档](https://stripe.com/docs/upgrades#what-changes-does-stripe-consider-to-be-backwards-compatible)。

<a name="configuration"></a>
## 配置

<a name="billable-model"></a>
### 可计费模型

使用 Cashier 之前，请在可计费模型的定义中添加 `Billable` trait，通常就是 `App\Models\User` 模型。该 trait 提供了多种方法，让你执行常见的计费任务，例如创建订阅、应用优惠券和更新支付方式信息：

```php
use Laravel\Cashier\Billable;

class User extends Authenticatable
{
    use Billable;
}
```

Cashier 默认使用 Laravel 自带的 `App\Models\User` 类作为可计费模型。如果希望更改，可以通过 `useCustomerModel` 方法指定其他模型。通常应在 `AppServiceProvider` 类的 `boot` 方法中调用此方法：

```php
use App\Models\Cashier\User;
use Laravel\Cashier\Cashier;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Cashier::useCustomerModel(User::class);
}
```

> [!WARNING]
> 如果你使用的模型不是 Laravel 提供的 `App\Models\User`，则需要发布并修改 [Cashier 迁移](#installation)，使其表名与你的模型相匹配。

<a name="api-keys"></a>
### API 密钥

接下来，在应用的 `.env` 文件中配置 Stripe API 密钥。你可以从 Stripe 控制面板获取这些密钥：

```ini
STRIPE_KEY=your-stripe-key
STRIPE_SECRET=your-stripe-secret
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
```

> [!WARNING]
> 请确保在应用的 `.env` 文件中定义了 `STRIPE_WEBHOOK_SECRET` 环境变量，它用于验证传入的 Webhook 确实来自 Stripe。

<a name="currency-configuration"></a>
### 货币配置

Cashier 默认使用美元（USD）。你可以在应用的 `.env` 文件中设置 `CASHIER_CURRENCY` 环境变量来更改默认货币：

```ini
CASHIER_CURRENCY=eur
```

除了配置 Cashier 的货币，你还可以指定语言区域，用于格式化发票上显示的金额。Cashier 在内部使用 [PHP 的 `NumberFormatter` 类](https://www.php.net/manual/en/class.numberformatter.php) 设置货币的语言区域：

```ini
CASHIER_CURRENCY_LOCALE=nl_BE
```

> [!WARNING]
> 要使用 `en` 之外的语言区域，请确保服务器已安装并配置 `ext-intl` PHP 扩展。

<a name="tax-configuration"></a>
### 税务配置

借助 [Stripe Tax](https://stripe.com/tax)，你可以为 Stripe 生成的所有发票自动计算税费。在应用的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用 `calculateTaxes` 方法，即可启用自动税费计算：

```php
use Laravel\Cashier\Cashier;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Cashier::calculateTaxes();
}
```

启用后，所有新订阅和新生成的一次性发票都会自动计算税费。

要让此功能正常工作，需要将客户的账单信息（如姓名、地址和税号）同步到 Stripe。你可以使用 Cashier 提供的 [客户数据同步](#syncing-customer-data-with-stripe) 和 [税号](#tax-ids) 方法完成同步。

<a name="logging"></a>
### 日志记录

Cashier 允许你指定记录 Stripe 严重错误时使用的日志通道。在应用的 `.env` 文件中定义 `CASHIER_LOGGER` 环境变量即可指定：

```ini
CASHIER_LOGGER=stack
```

调用 Stripe API 产生的异常会通过应用的默认日志通道记录。

<a name="using-custom-models"></a>
### 使用自定义模型

你可以定义自己的模型，并继承相应的 Cashier 模型，来扩展 Cashier 内部使用的模型：

```php
use Laravel\Cashier\Subscription as CashierSubscription;

class Subscription extends CashierSubscription
{
    // ...
}
```

定义模型后，可以通过 `Laravel\Cashier\Cashier` 类让 Cashier 使用自定义模型。通常应在应用的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中完成配置：

```php
use App\Models\Cashier\Subscription;
use App\Models\Cashier\SubscriptionItem;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Cashier::useSubscriptionModel(Subscription::class);
    Cashier::useSubscriptionItemModel(SubscriptionItem::class);
}
```

<a name="quickstart"></a>
## 快速入门

<a name="quickstart-selling-products"></a>
### 销售产品

> [!NOTE]
> 使用 Stripe Checkout 之前，应先在 Stripe 控制面板中定义具有固定价格的产品，并 [配置 Cashier 的 Webhook 处理](#handling-stripe-webhooks)。

为应用提供产品销售和订阅计费功能可能让人望而却步，但借助 Cashier 和 [Stripe Checkout](https://stripe.com/payments/checkout)，你可以轻松构建现代、可靠的支付集成。

对于非循环、仅收费一次的产品，我们会使用 Cashier 将客户引导到 Stripe Checkout，让客户填写支付信息并确认购买。通过 Checkout 完成付款后，客户会被重定向到你在应用中指定的成功页面 URL：

```php
use Illuminate\Http\Request;

Route::get('/checkout', function (Request $request) {
    $stripePriceId = 'price_deluxe_album';

    $quantity = 1;

    return $request->user()->checkout([$stripePriceId => $quantity], [
        'success_url' => route('checkout-success'),
        'cancel_url' => route('checkout-cancel'),
    ]);
})->name('checkout');

Route::view('/checkout/success', 'checkout.success')->name('checkout-success');
Route::view('/checkout/cancel', 'checkout.cancel')->name('checkout-cancel');
```

如上例所示，我们使用 Cashier 提供的 `checkout` 方法，根据给定的「价格标识符」将客户重定向到 Stripe Checkout。在 Stripe 中，「价格」指的是 [为特定产品定义的价格](https://stripe.com/docs/products-prices/how-products-and-prices-work)。

必要时，`checkout` 方法会自动在 Stripe 中创建客户，并将该 Stripe 客户记录与应用数据库中的相应用户关联。结账会话结束后，客户会被重定向到专门的成功或取消页面，你可以在这些页面上向客户显示提示信息。

<a name="providing-meta-data-to-stripe-checkout"></a>
#### 向 Stripe Checkout 提供元数据

销售产品时，通常会使用应用自行定义的 `Cart` 和 `Order` 模型来跟踪已完成的订单和已购买的产品。将客户重定向到 Stripe Checkout 完成购买时，你可能需要提供现有订单的标识符，以便客户返回应用后，将已完成的购买与相应订单关联起来。

为此，你可以向 `checkout` 方法传入一个 `metadata` 数组。假设用户开始结账时，应用会创建一个待处理的 `Order`。请注意，示例中的 `Cart` 和 `Order` 模型仅用于说明，并非由 Cashier 提供；你可以根据应用需求自行实现：

```php
use App\Models\Cart;
use App\Models\Order;
use Illuminate\Http\Request;

Route::get('/cart/{cart}/checkout', function (Request $request, Cart $cart) {
    $order = Order::create([
        'cart_id' => $cart->id,
        'price_ids' => $cart->price_ids,
        'status' => 'incomplete',
    ]);

    return $request->user()->checkout($order->price_ids, [
        'success_url' => route('checkout-success').'?session_id={CHECKOUT_SESSION_ID}',
        'cancel_url' => route('checkout-cancel'),
        'metadata' => ['order_id' => $order->id],
    ]);
})->name('checkout');
```

如上例所示，用户开始结账时，我们会将购物车或订单关联的所有 Stripe 价格标识符传给 `checkout` 方法。客户添加商品时，应用负责将商品与「购物车」或订单关联。我们还通过 `metadata` 数组将订单 ID 传给 Stripe Checkout 会话。最后，在结账成功路由中添加了 `CHECKOUT_SESSION_ID` 模板变量。当 Stripe 将客户重定向回应用时，此变量会自动替换为结账会话 ID。

接下来，创建结账成功路由。用户通过 Stripe Checkout 完成购买后会被重定向到此路由。在路由中，我们可以获取 Stripe Checkout 会话 ID 及相应的 Stripe Checkout 实例，读取之前提供的元数据，并据此更新客户订单：

```php
use App\Models\Order;
use Illuminate\Http\Request;
use Laravel\Cashier\Cashier;

Route::get('/checkout/success', function (Request $request) {
    $sessionId = $request->get('session_id');

    if ($sessionId === null) {
        return;
    }

    $session = Cashier::stripe()->checkout->sessions->retrieve($sessionId);

    if ($session->payment_status !== 'paid') {
        return;
    }

    $orderId = $session['metadata']['order_id'] ?? null;

    $order = Order::findOrFail($orderId);

    $order->update(['status' => 'completed']);

    return view('checkout-success', ['order' => $order]);
})->name('checkout-success');
```

有关 [Checkout 会话对象所包含的数据](https://stripe.com/docs/api/checkout/sessions/object)，请参阅 Stripe 文档。

<a name="quickstart-selling-subscriptions"></a>
### 销售订阅

> [!NOTE]
> 使用 Stripe Checkout 之前，应先在 Stripe 控制面板中定义具有固定价格的产品，并 [配置 Cashier 的 Webhook 处理](#handling-stripe-webhooks)。

为应用提供产品销售和订阅计费功能可能让人望而却步，但借助 Cashier 和 [Stripe Checkout](https://stripe.com/payments/checkout)，你可以轻松构建现代、可靠的支付集成。

为了了解如何使用 Cashier 和 Stripe Checkout 销售订阅，我们以一个简单的订阅服务为例：它提供基础月付方案（`price_basic_monthly`）和年付方案（`price_basic_yearly`），这两个价格可以归在 Stripe 控制面板的「Basic」产品（`pro_basic`）下。此外，该服务还可能提供 Expert 方案，对应产品 `pro_expert`。

首先，看看客户如何订阅服务。客户可能会在应用的定价页面点击 Basic 方案的「订阅」按钮。该按钮或链接应将用户引导至一个 Laravel 路由，为其所选方案创建 Stripe Checkout 会话：

```php
use Illuminate\Http\Request;

Route::get('/subscription-checkout', function (Request $request) {
    return $request->user()
        ->newSubscription('default', 'price_basic_monthly')
        ->trialDays(5)
        ->allowPromotionCodes()
        ->checkout([
            'success_url' => route('your-success-route'),
            'cancel_url' => route('your-cancel-route'),
        ]);
});
```

如上例所示，客户会被重定向到 Stripe Checkout 会话，以订阅 Basic 方案。结账成功或取消后，客户会被重定向回传给 `checkout` 方法的 URL。由于某些支付方式需要几秒钟才能处理完毕，我们还需要 [配置 Cashier 的 Webhook 处理](#handling-stripe-webhooks)，以确定订阅何时真正开始。

现在客户已能创建订阅，我们需要限制应用的部分功能，让它们仅对已订阅用户开放。你可以通过 Cashier 的 `Billable` trait 提供的 `subscribed` 方法，判断用户当前的订阅状态：

```blade
@if ($user->subscribed())
    <p>You are subscribed.</p>
@endif
```

我们还可以轻松判断用户是否订阅了特定的产品或价格：

```blade
@if ($user->subscribedToProduct('pro_basic'))
    <p>You are subscribed to our Basic product.</p>
@endif

@if ($user->subscribedToPrice('price_basic_monthly'))
    <p>You are subscribed to our monthly Basic plan.</p>
@endif
```

<a name="quickstart-building-a-subscribed-middleware"></a>
#### 构建订阅验证中间件

为了便于复用，你可以创建一个 [中间件](/docs/{{version}}/middleware)，判断传入请求是否来自已订阅用户。定义后，将它分配给路由即可阻止未订阅用户访问：

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class Subscribed
{
    /**
     * 处理传入的请求。
     */
    public function handle(Request $request, Closure $next): Response
    {
        if (! $request->user()?->subscribed()) {
            // 将用户重定向到账单页面，并提示其订阅……
            return redirect('/billing');
        }

        return $next($request);
    }
}
```

定义中间件后，可以将其分配给路由：

```php
use App\Http\Middleware\Subscribed;

Route::get('/dashboard', function () {
    // ...
})->middleware([Subscribed::class]);
```

<a name="quickstart-allowing-customers-to-manage-their-billing-plan"></a>
#### 允许客户管理计费方案

客户可能希望将订阅方案切换为其他产品或「等级」。最简单的实现方式是将客户引导到 Stripe 的 [客户账单门户](https://stripe.com/docs/no-code/customer-portal)。该门户提供托管界面，让客户下载发票、更新支付方式和更改订阅方案。

首先，在应用中定义一个链接或按钮，将用户引导到用于创建账单门户会话的 Laravel 路由：

```blade
<a href="{{ route('billing') }}">
    Billing
</a>
```

接下来，定义创建 Stripe 客户账单门户会话的路由，并将用户重定向到该门户。`redirectToBillingPortal` 方法接收一个 URL，用户退出门户后会返回此地址：

```php
use Illuminate\Http\Request;

Route::get('/billing', function (Request $request) {
    return $request->user()->redirectToBillingPortal(route('dashboard'));
})->middleware(['auth'])->name('billing');
```

> [!NOTE]
> 只要配置了 Cashier 的 Webhook 处理，Cashier 就会检查来自 Stripe 的 Webhook，自动保持应用中与 Cashier 相关的数据表同步。例如，用户通过 Stripe 客户账单门户取消订阅时，Cashier 会收到相应的 Webhook，并在应用数据库中将订阅标记为「已取消」。

<a name="customers"></a>
## 客户

<a name="retrieving-customers"></a>
### 获取客户

你可以使用 `Cashier::findBillable` 方法，通过 Stripe ID 获取客户。该方法会返回可计费模型的实例：

```php
use Laravel\Cashier\Cashier;

$user = Cashier::findBillable($stripeId);
```

<a name="creating-customers"></a>
### 创建客户

有时，你可能希望创建 Stripe 客户，但暂不创建订阅。可以使用 `createAsStripeCustomer` 方法：

```php
$stripeCustomer = $user->createAsStripeCustomer();
```

在 Stripe 中创建客户后，你可以在之后的任意时间创建订阅。还可以传入可选的 `$options` 数组，提供额外的 [Stripe API 支持的客户创建参数](https://stripe.com/docs/api/customers/create)：

```php
$stripeCustomer = $user->createAsStripeCustomer($options);
```

如果希望获取可计费模型对应的 Stripe 客户对象，可以使用 `asStripeCustomer` 方法：

```php
$stripeCustomer = $user->asStripeCustomer();
```

如果希望获取给定可计费模型的 Stripe 客户对象，但不确定它是否已是 Stripe 中的客户，可以使用 `createOrGetStripeCustomer` 方法。若客户不存在，该方法会在 Stripe 中创建新客户：

```php
$stripeCustomer = $user->createOrGetStripeCustomer();
```

<a name="updating-customers"></a>
### 更新客户

有时，你可能希望直接为 Stripe 客户更新额外信息。可以使用 `updateStripeCustomer` 方法，该方法接收一个包含 [Stripe API 支持的客户更新选项](https://stripe.com/docs/api/customers/update) 的数组：

```php
$stripeCustomer = $user->updateStripeCustomer($options);
```

<a name="balances"></a>
### 余额

Stripe 允许你向客户「余额」记入贷项或借项，之后会在新发票中抵扣或加收。要查看客户的总余额，可以使用可计费模型上的 `balance` 方法。该方法会返回以客户所用货币格式化后的余额字符串：

```php
$balance = $user->balance();
```

要向客户余额记入贷项，可以向 `creditBalance` 方法传入一个金额。如果需要，还可以提供描述：

```php
$user->creditBalance(500, 'Premium customer top-up.');
```

向 `debitBalance` 方法传入金额，会向客户余额记入借项：

```php
$user->debitBalance(300, 'Bad usage penalty.');
```

`applyBalance` 方法会为客户创建新的余额交易记录。你可以使用 `balanceTransactions` 方法获取这些记录，向客户展示贷项和借项的变动日志：

```php
// 获取所有交易记录……
$transactions = $user->balanceTransactions();

foreach ($transactions as $transaction) {
    // 交易金额……
    $amount = $transaction->amount(); // $2.31

    // 获取关联发票（如果存在）……
    $invoice = $transaction->invoice();
}
```

<a name="tax-ids"></a>
### 税号

Cashier 提供了管理客户税号的简便方式。例如，`taxIds` 方法可以获取分配给客户的所有 [税号](https://stripe.com/docs/api/customer_tax_ids/object)，并返回一个集合：

```php
$taxIds = $user->taxIds();
```

你也可以通过标识符获取客户的某个税号：

```php
$taxId = $user->findTaxId('txi_belgium');
```

向 `createTaxId` 方法提供有效的 [类型](https://stripe.com/docs/api/customer_tax_ids/object#tax_id_object-type) 和值，即可创建新税号：

```php
$taxId = $user->createTaxId('eu_vat', 'BE0123456789');
```

`createTaxId` 方法会立即将增值税税号添加到客户账户。[Stripe 也会验证增值税税号](https://stripe.com/docs/invoicing/customer/tax-ids#validation)，但这是异步过程。你可以订阅 `customer.tax_id.updated` Webhook 事件，并检查 [税号的 `verification` 参数](https://stripe.com/docs/api/customer_tax_ids/object#tax_id_object-verification)，来获知验证状态的更新。有关处理 Webhook 的更多信息，请参阅 [定义 Webhook 处理器的文档](#handling-stripe-webhooks)。

可以使用 `deleteTaxId` 方法删除税号：

```php
$user->deleteTaxId('txi_belgium');
```

<a name="syncing-customer-data-with-stripe"></a>
### 向 Stripe 同步客户数据

通常，当应用用户更新姓名、电子邮件地址或其他同样存储在 Stripe 中的信息时，你应通知 Stripe 这些变更，使 Stripe 中的信息与应用保持同步。

要自动完成同步，可以在可计费模型上定义一个响应模型 `updated` 事件的监听器，并在监听器中调用模型的 `syncStripeCustomerDetails` 方法：

```php
use App\Models\User;
use function Illuminate\Events\queueable;

/**
 * 模型的「booted」方法。
 */
protected static function booted(): void
{
    static::updated(queueable(function (User $customer) {
        if ($customer->hasStripeId()) {
            $customer->syncStripeCustomerDetails();
        }
    }));
}
```

现在，每次客户模型更新时，其信息都会同步到 Stripe。为方便起见，Cashier 也会在客户首次创建时自动向 Stripe 同步信息。

你可以重写 Cashier 提供的多种方法，自定义向 Stripe 同步客户信息时使用的字段。例如，重写 `stripeName` 方法，可以指定 Cashier 同步信息时，哪个属性应作为客户的「姓名」：

```php
/**
 * 获取应同步到 Stripe 的客户姓名。
 */
public function stripeName(): string|null
{
    return $this->company_name;
}
```

同样，你可以重写 `stripeEmail`、`stripePhone`（最多 20 个字符）、`stripeAddress` 和 `stripePreferredLocales` 方法。[更新 Stripe 客户对象](https://stripe.com/docs/api/customers/update) 时，这些方法会将信息同步到相应的客户参数。如果希望完全控制客户信息的同步过程，可以重写 `syncStripeCustomerDetails` 方法。

<a name="billing-portal"></a>
### 账单门户

Stripe 提供了 [设置账单门户的简便方式](https://stripe.com/docs/billing/subscriptions/customer-portal)，让客户管理订阅、支付方式并查看账单历史。在控制器或路由中调用可计费模型的 `redirectToBillingPortal` 方法，即可将用户重定向到账单门户：

```php
use Illuminate\Http\Request;

Route::get('/billing-portal', function (Request $request) {
    return $request->user()->redirectToBillingPortal();
});
```

默认情况下，用户完成订阅管理后，可以通过 Stripe 账单门户中的链接返回应用的 `home` 路由。你也可以将自定义 URL 作为参数传给 `redirectToBillingPortal` 方法，指定用户返回的地址：

```php
use Illuminate\Http\Request;

Route::get('/billing-portal', function (Request $request) {
    return $request->user()->redirectToBillingPortal(route('billing'));
});
```

如果只希望生成账单门户 URL，而不生成 HTTP 重定向响应，可以调用 `billingPortalUrl` 方法：

```php
$url = $request->user()->billingPortalUrl(route('billing'));
```

<a name="payment-methods"></a>
## 支付方式

<a name="storing-payment-methods"></a>
### 存储支付方式

要通过 Stripe 创建订阅或执行「一次性」收费，应用需要安全地收集客户的支付信息。根据你是打算保存支付方式以供未来订阅使用，还是立即处理单次收费，实现方式会有所不同。下面分别介绍这两种情况。

Stripe 的 [Payment Element](https://stripe.com/docs/payments/payment-element) 支持多种支付方式，例如银行卡、Apple Pay、Google Pay 和 iDEAL。

<a name="payment-element-for-subscriptions"></a>
#### 用于订阅的 Payment Element

首先，创建一个 Setup Intent，并将其传给视图：

```php
return view('subscribe', [
    'intent' => $user->createSetupIntent()
]);
```

使用 Setup Intent 的 `client_secret` 挂载 Payment Element：

```html
<div id="payment-element"></div>
<button id="submit">Subscribe</button>

<script src="https://js.stripe.com/v3/"></script>
<script>
    const stripe = Stripe('stripe-public-key');

    const elements = stripe.elements({
        clientSecret: '{{ $intent->client_secret }}'
    });

    const paymentElement = elements.create('payment');

    paymentElement.mount('#payment-element');

    document.getElementById('submit').addEventListener('click', async () => {
        const { error } = await stripe.confirmSetup({
            elements,
            confirmParams: {
                return_url: '{{ route("subscription.complete") }}',
            },
        });

        if (error) {
            // 向用户显示「error.message」……
        }
    });
</script>
```

Stripe 重定向到 `return_url` 后，你可以从查询字符串参数中取得 `setup_intent` ID，并使用该值获取支付方式和创建订阅：

```php
use Illuminate\Http\Request;

Route::get('/subscription/complete', function (Request $request) {
    $setupIntent = $request->user()->findSetupIntent(
        $request->setup_intent
    );

    $paymentMethod = $setupIntent->payment_method;

    $request->user()
        ->newSubscription('default', 'price_xxx')
        ->create($paymentMethod);

    return redirect('/dashboard');
})->name('subscription.complete');
```

如果使用 Payment Element 的目的是更新客户的默认支付方式，而不是创建订阅，可以将支付方式标识符传给 [`updateDefaultPaymentMethod`](#updating-the-default-payment-method) 方法。

<a name="payment-element-for-single-charges"></a>
#### 用于单次收费的 Payment Element

对于一次性支付，使用 Cashier 的 `pay` 方法创建支付意向（Payment Intent）。通常应在应用的相应订单中存储 Payment Intent ID，以便 Stripe 将客户重定向回应用后，能够找到该订单。以下示例假设应用中有一个 `Order` 模型，包含 `user_id`、`amount`、`status` 和 `stripe_payment_intent_id` 列：

```php
use App\Models\Order;
use Illuminate\Http\Request;

Route::post('/pay', function (Request $request) {
    $amount = 1000;

    $payment = $request->user()->pay($amount);

    $order = Order::create([
        'user_id' => $request->user()->id,
        'amount' => $amount,
        'status' => 'pending',
        'stripe_payment_intent_id' => $payment->id,
    ]);

    return view('checkout', [
        'clientSecret' => $payment->client_secret,
        'order' => $order,
    ]);
});
```

然后，挂载 Payment Element 并确认支付：

```html
<div id="payment-element"></div>
<button id="submit">Pay Now</button>

<script src="https://js.stripe.com/v3/"></script>
<script>
    const stripe = Stripe('stripe-public-key');

    const elements = stripe.elements({
        clientSecret: '{{ $clientSecret }}'
    });

    const paymentElement = elements.create('payment');

    paymentElement.mount('#payment-element');

    document.getElementById('submit').addEventListener('click', async () => {
        const { error } = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: '{{ route("payment.complete") }}',
            },
        });

        if (error) {
            // 向用户显示「error.message」……
        }
    });
</script>
```

重定向后，可以通过查询字符串中的 `payment_intent` 参数获取相应订单和 Payment Intent。履行订单之前，应确认订单属于当前已认证客户，并验证 Payment Intent 同样属于该客户且支付已成功：

```php
use App\Models\Order;
use Illuminate\Http\Request;

Route::get('/payment/complete', function (Request $request) {
    $order = Order::where('user_id', $request->user()->id)
        ->where('stripe_payment_intent_id', $request->payment_intent)
        ->firstOrFail();

    $paymentIntent = $request->user()
        ->stripe()
        ->paymentIntents
        ->retrieve($request->payment_intent);

    if ($paymentIntent->customer === $request->user()->stripe_id &&
        $paymentIntent->status === 'succeeded') {
        $order->update(['status' => 'paid']);

        // 履行订单……
    }

    return redirect('/dashboard');
})->name('payment.complete');
```

<a name="retrieving-payment-methods"></a>
### 获取支付方式

可计费模型实例上的 `paymentMethods` 方法会返回由 `Laravel\Cashier\PaymentMethod` 实例组成的集合：

```php
$paymentMethods = $user->paymentMethods();
```

默认情况下，该方法会返回所有类型的支付方式。若要获取特定类型，可以将 `type` 作为参数传给该方法：

```php
$paymentMethods = $user->paymentMethods('sepa_debit');
```

要获取客户的默认支付方式，可以使用 `defaultPaymentMethod` 方法：

```php
$paymentMethod = $user->defaultPaymentMethod();
```

你可以使用 `findPaymentMethod` 方法获取已附加到可计费模型的某个支付方式：

```php
$paymentMethod = $user->findPaymentMethod($paymentMethodId);
```

<a name="payment-method-presence"></a>
### 检查支付方式是否存在

要判断可计费模型的账户是否附加了默认支付方式，可以调用 `hasDefaultPaymentMethod` 方法：

```php
if ($user->hasDefaultPaymentMethod()) {
    // ...
}
```

你可以使用 `hasPaymentMethod` 方法，判断可计费模型的账户是否附加了至少一种支付方式：

```php
if ($user->hasPaymentMethod()) {
    // ...
}
```

该方法会检查可计费模型是否拥有任何支付方式。若要判断是否存在特定类型的支付方式，可以将 `type` 作为参数传给该方法：

```php
if ($user->hasPaymentMethod('sepa_debit')) {
    // ...
}
```

<a name="updating-the-default-payment-method"></a>
### 更新默认支付方式

`updateDefaultPaymentMethod` 方法用于更新客户的默认支付方式信息。它接收 Stripe 支付方式标识符，并将新的支付方式设为默认计费支付方式：

```php
$user->updateDefaultPaymentMethod($paymentMethod);
```

要将本地默认支付方式信息与 Stripe 中客户的默认支付方式同步，可以使用 `updateDefaultPaymentMethodFromStripe` 方法：

```php
$user->updateDefaultPaymentMethodFromStripe();
```

> [!WARNING]
> 客户的默认支付方式只能用于开具发票和创建新订阅。由于 Stripe 的限制，它不能用于单次收费。

<a name="adding-payment-methods"></a>
### 添加支付方式

要添加新的支付方式，可以在可计费模型上调用 `addPaymentMethod` 方法，并传入支付方式标识符：

```php
$user->addPaymentMethod($paymentMethod);
```

> [!NOTE]
> 要了解如何获取支付方式标识符，请参阅 [支付方式存储文档](#storing-payment-methods)。

<a name="deleting-payment-methods"></a>
### 删除支付方式

要删除支付方式，可以在相应的 `Laravel\Cashier\PaymentMethod` 实例上调用 `delete` 方法：

```php
$paymentMethod->delete();
```

`deletePaymentMethod` 方法会从可计费模型中删除指定的支付方式：

```php
$user->deletePaymentMethod('pm_visa');
```

`deletePaymentMethods` 方法会删除可计费模型的所有支付方式信息：

```php
$user->deletePaymentMethods();
```

默认情况下，该方法会删除所有类型的支付方式。若只删除特定类型，可以将 `type` 作为参数传给该方法：

```php
$user->deletePaymentMethods('sepa_debit');
```

> [!WARNING]
> 如果用户拥有有效订阅，应用不应允许其删除默认支付方式。

<a name="subscriptions"></a>
## 订阅

订阅让你可以为客户设置定期付款。Cashier 管理的 Stripe 订阅支持多个订阅价格、订阅数量、试用期等功能。

<a name="creating-subscriptions"></a>
### 创建订阅

要创建订阅，首先获取可计费模型实例，通常是 `App\Models\User` 实例。然后，使用 `newSubscription` 方法为该模型创建订阅：

```php
use Illuminate\Http\Request;

Route::post('/user/subscribe', function (Request $request) {
    $request->user()->newSubscription(
        'default', 'price_monthly'
    )->create($request->paymentMethodId);

    // ...
});
```

传给 `newSubscription` 方法的第一个参数应是订阅的内部类型。如果应用只提供一种订阅，可以将其命名为 `default` 或 `primary`。此类型仅供应用内部使用，不用于向用户展示；它不应包含空格，且创建订阅后绝不能更改。第二个参数是用户订阅的具体价格，应与 Stripe 中的价格标识符对应。

`create` 方法接收 [Stripe 支付方式标识符](#storing-payment-methods) 或 Stripe `PaymentMethod` 对象。它会启动订阅，并在数据库中更新可计费模型的 Stripe 客户 ID 及其他相关计费信息。

> [!WARNING]
> 直接向创建订阅的 `create` 方法传入支付方式标识符，也会自动将该支付方式加入用户保存的支付方式中。

<a name="collecting-recurring-payments-via-invoice-emails"></a>
#### 通过发票邮件收取定期付款

你可以让 Stripe 在每次定期付款到期时，向客户发送发票邮件，而不自动扣款。客户收到发票后可手动付款。通过发票收取定期付款时，客户无需预先提供支付方式：

```php
$user->newSubscription('default', 'price_monthly')->createAndSendInvoice();
```

`days_until_due` 选项决定客户在订阅被取消前有多少天可以支付发票。默认是 30 天，你也可以根据需要指定其他值：

```php
$user->newSubscription('default', 'price_monthly')->createAndSendInvoice([], [
    'days_until_due' => 30
]);
```

<a name="subscription-quantities"></a>
#### 数量

如果希望在创建订阅时为价格设置特定的 [数量](https://stripe.com/docs/billing/subscriptions/quantities)，应在创建订阅前，在订阅构建器上调用 `quantity` 方法：

```php
$user->newSubscription('default', 'price_monthly')
    ->quantity(5)
    ->create($paymentMethod);
```

<a name="additional-details"></a>
#### 其他详细信息

如果希望指定 Stripe 支持的额外 [客户](https://stripe.com/docs/api/customers/create) 或 [订阅](https://stripe.com/docs/api/subscriptions/create) 选项，可以分别将其作为第二个和第三个参数传给 `create` 方法：

```php
$user->newSubscription('default', 'price_monthly')->create($paymentMethod, [
    'email' => $email,
], [
    'metadata' => ['note' => 'Some extra information.'],
]);
```

<a name="coupons"></a>
#### 优惠券

如果希望在创建订阅时应用优惠券，可以使用 `withCoupon` 方法：

```php
$user->newSubscription('default', 'price_monthly')
    ->withCoupon('code')
    ->create($paymentMethod);
```

如果希望应用 [Stripe 促销码](https://stripe.com/docs/billing/subscriptions/discounts/codes)，可以使用 `withPromotionCode` 方法：

```php
$user->newSubscription('default', 'price_monthly')
    ->withPromotionCode('promo_code_id')
    ->create($paymentMethod);
```

这里的促销码 ID 应是 Stripe 分配给促销码的 API ID，而不是客户看到的促销码。如果需要根据面向客户的促销码查找其 ID，可以使用 `findPromotionCode` 方法：

```php
// 根据面向客户的促销码查找其 ID……
$promotionCode = $user->findPromotionCode('SUMMERSALE');

// 根据面向客户的促销码查找当前有效的促销码 ID……
$promotionCode = $user->findActivePromotionCode('SUMMERSALE');
```

上例返回的 `$promotionCode` 对象是 `Laravel\Cashier\PromotionCode` 实例，该类封装了底层的 `Stripe\PromotionCode` 对象。调用 `coupon` 方法可以获取促销码关联的优惠券：

```php
$coupon = $user->findPromotionCode('SUMMERSALE')->coupon();
```

通过优惠券实例，你可以判断折扣金额，以及优惠券采用的是固定金额折扣还是百分比折扣：

```php
if ($coupon->isPercentage()) {
    return $coupon->percentOff().'%'; // 21.5%
} else {
    return $coupon->amountOff(); // $5.99
}
```

你还可以获取当前应用于客户或订阅的折扣：

```php
$discount = $billable->discount();

$discount = $subscription->discount();
```

返回的 `Laravel\Cashier\Discount` 实例封装了底层的 `Stripe\Discount` 对象。调用 `coupon` 方法可以获取该折扣关联的优惠券：

```php
$coupon = $subscription->discount()->coupon();
```

如果希望为客户或订阅应用新的优惠券或促销码，可以使用 `applyCoupon` 或 `applyPromotionCode` 方法：

```php
$billable->applyCoupon('coupon_id');
$billable->applyPromotionCode('promotion_code_id');

$subscription->applyCoupon('coupon_id');
$subscription->applyPromotionCode('promotion_code_id');
```

请记住，应使用 Stripe 分配给促销码的 API ID，而不是客户看到的促销码。同一时间，一个客户或订阅只能应用一张优惠券或一个促销码。

更多信息请参阅 Stripe 关于 [优惠券](https://stripe.com/docs/billing/subscriptions/coupons) 和 [促销码](https://stripe.com/docs/billing/subscriptions/coupons/codes) 的文档。

<a name="adding-subscriptions"></a>
#### 添加订阅

如果希望为已经拥有默认支付方式的客户添加订阅，可以在订阅构建器上调用 `add` 方法：

```php
use App\Models\User;

$user = User::find(1);

$user->newSubscription('default', 'price_monthly')->add();
```

<a name="creating-subscriptions-from-the-stripe-dashboard"></a>
#### 从 Stripe 控制面板创建订阅

你也可以直接在 Stripe 控制面板中创建订阅。Cashier 会同步新增订阅，并为其分配 `default` 类型。要自定义通过控制面板创建的订阅类型，可以 [定义 Webhook 事件处理器](#defining-webhook-event-handlers)。

此外，通过 Stripe 控制面板只能创建一种类型的订阅。如果应用提供多种不同类型的订阅，只有其中一种可以通过 Stripe 控制面板添加。

最后，应始终确保每个客户在应用提供的每种订阅类型下，最多只有一个有效订阅。如果客户有两个 `default` 订阅，即使两者都会同步到应用数据库，Cashier 也只会使用最近添加的订阅。

<a name="checking-subscription-status"></a>
### 检查订阅状态

客户订阅应用后，你可以使用多种便捷方法检查其订阅状态。首先，只要客户拥有有效订阅，即使仍在试用期内，`subscribed` 方法也会返回 `true`。该方法的第一个参数是订阅类型：

```php
if ($user->subscribed('default')) {
    // ...
}
```

`subscribed` 方法也很适合用于 [路由中间件](/docs/{{version}}/middleware)，以根据用户的订阅状态控制其对路由和控制器的访问：

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureUserIsSubscribed
{
    /**
     * 处理传入的请求。
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        if ($request->user() && ! $request->user()->subscribed('default')) {
            // 此用户不是付费客户……
            return redirect('/billing');
        }

        return $next($request);
    }
}
```

如果希望判断用户是否仍处于试用期，可以使用 `onTrial` 方法。这有助于决定是否向用户显示仍在试用期的提示：

```php
if ($user->subscription('default')->onTrial()) {
    // ...
}
```

`subscribedToProduct` 方法可以根据 Stripe 产品标识符，判断用户是否订阅了给定产品。在 Stripe 中，一个产品可以包含一组价格。以下示例判断用户的 `default` 订阅是否是应用「premium」产品的有效订阅。传入的产品标识符应对应 Stripe 控制面板中的某个产品：

```php
if ($user->subscribedToProduct('prod_premium', 'default')) {
    // ...
}
```

向 `subscribedToProduct` 方法传入数组，可以判断用户的 `default` 订阅是否是应用「basic」或「premium」产品的有效订阅：

```php
if ($user->subscribedToProduct(['prod_basic', 'prod_premium'], 'default')) {
    // ...
}
```

`subscribedToPrice` 方法可以判断客户的订阅是否对应给定的价格 ID：

```php
if ($user->subscribedToPrice('price_basic_monthly', 'default')) {
    // ...
}
```

`recurring` 方法可以判断用户当前是否已订阅，且已不在试用期内：

```php
if ($user->subscription('default')->recurring()) {
    // ...
}
```

> [!WARNING]
> 如果用户有两个相同类型的订阅，`subscription` 方法始终返回最新的订阅。例如，用户可能有两条类型为 `default` 的订阅记录，其中一条是旧的、已过期的订阅，另一条是当前有效的订阅。该方法始终返回最新订阅，旧订阅则保留在数据库中供历史查询。

<a name="cancelled-subscription-status"></a>
#### 已取消订阅的状态

要判断用户是否曾是有效订阅者，但已取消订阅，可以使用 `canceled` 方法：

```php
if ($user->subscription('default')->canceled()) {
    // ...
}
```

你也可以判断用户是否已取消订阅，但在订阅完全到期前仍处于「宽限期」。例如，用户在 3 月 5 日取消了原定于 3 月 10 日到期的订阅，那么在 3 月 10 日之前仍处于宽限期。请注意，此期间 `subscribed` 方法仍返回 `true`：

```php
if ($user->subscription('default')->onGracePeriod()) {
    // ...
}
```

要判断用户是否已取消订阅且不再处于「宽限期」，可以使用 `ended` 方法：

```php
if ($user->subscription('default')->ended()) {
    // ...
}
```

<a name="incomplete-and-past-due-status"></a>
#### 未完成和逾期状态

如果订阅创建后需要额外的支付操作，订阅会被标记为 `incomplete`。订阅状态存储在 Cashier 的 `subscriptions` 数据表的 `stripe_status` 列中。

同样，如果切换价格时需要额外的支付操作，订阅会被标记为 `past_due`。订阅处于这两种状态之一时，必须等客户确认支付后才会生效。你可以在可计费模型或订阅实例上使用 `hasIncompletePayment` 方法，判断订阅是否有未完成的支付：

```php
if ($user->hasIncompletePayment('default')) {
    // ...
}

if ($user->subscription('default')->hasIncompletePayment()) {
    // ...
}
```

订阅存在未完成支付时，应将用户引导到 Cashier 的支付确认页面，并传入 `latestPayment` 的标识符。可以通过订阅实例上的 `latestPayment` 方法获取该标识符：

```html
<a href="{{ route('cashier.payment', $subscription->latestPayment()->id) }}">
    Please confirm your payment.
</a>
```

如果希望订阅在 `past_due` 或 `incomplete` 状态下仍被视为有效，可以使用 Cashier 提供的 `keepPastDueSubscriptionsActive` 和 `keepIncompleteSubscriptionsActive` 方法。通常应在 `App\Providers\AppServiceProvider` 的 `register` 方法中调用：

```php
use Laravel\Cashier\Cashier;

/**
 * 注册应用服务。
 */
public function register(): void
{
    Cashier::keepPastDueSubscriptionsActive();
    Cashier::keepIncompleteSubscriptionsActive();
}
```

> [!WARNING]
> 订阅处于 `incomplete` 状态时，确认支付前不能修改。因此，此状态下调用 `swap` 和 `updateQuantity` 方法会抛出异常。

<a name="subscription-scopes"></a>
#### 订阅查询作用域

大多数订阅状态也可作为查询作用域使用，让你方便地从数据库中查询处于指定状态的订阅：

```php
// 获取所有有效订阅……
$subscriptions = Subscription::query()->active()->get();

// 获取用户的所有已取消订阅……
$subscriptions = $user->subscriptions()->canceled()->get();
```

可用查询作用域的完整列表如下：

```php
Subscription::query()->active();
Subscription::query()->canceled();
Subscription::query()->ended();
Subscription::query()->incomplete();
Subscription::query()->notCanceled();
Subscription::query()->notOnGracePeriod();
Subscription::query()->notOnTrial();
Subscription::query()->onGracePeriod();
Subscription::query()->onTrial();
Subscription::query()->pastDue();
Subscription::query()->recurring();
```

<a name="changing-prices"></a>
### 更改价格

客户订阅应用后，有时可能希望切换到新的订阅价格。将 Stripe 价格标识符传给 `swap` 方法即可切换。如果订阅之前已取消，切换价格时会假定用户希望重新激活订阅。传入的标识符应对应 Stripe 控制面板中的某个价格：

```php
use App\Models\User;

$user = App\Models\User::find(1);

$user->subscription('default')->swap('price_yearly');
```

如果客户处于试用期，试用期会保留。如果订阅设置了「数量」，该数量也会保留。

如果希望在切换价格时同时取消客户当前的试用期，可以调用 `skipTrial` 方法：

```php
$user->subscription('default')
    ->skipTrial()
    ->swap('price_yearly');
```

如果希望切换价格后立即向客户开具发票，而不等待下一个计费周期，可以使用 `swapAndInvoice` 方法：

```php
$user = User::find(1);

$user->subscription('default')->swapAndInvoice('price_yearly');
```

<a name="prorations"></a>
#### 按比例分摊

默认情况下，切换价格时 Stripe 会按比例分摊费用。使用 `noProrate` 方法可以在更新订阅价格时不进行费用分摊：

```php
$user->subscription('default')->noProrate()->swap('price_yearly');
```

有关订阅费用按比例分摊的更多信息，请参阅 [Stripe 文档](https://stripe.com/docs/billing/subscriptions/prorations)。

> [!WARNING]
> 在 `swapAndInvoice` 方法之前调用 `noProrate` 不会影响费用分摊，仍会开具发票。

<a name="subscription-quantity"></a>
### 订阅数量

有些订阅的收费取决于「数量」。例如，项目管理应用可能按每个项目每月 10 美元收费。你可以使用 `incrementQuantity` 和 `decrementQuantity` 方法增加或减少订阅数量：

```php
use App\Models\User;

$user = User::find(1);

$user->subscription('default')->incrementQuantity();

// 在订阅当前数量上增加 5……
$user->subscription('default')->incrementQuantity(5);

$user->subscription('default')->decrementQuantity();

// 在订阅当前数量上减少 5……
$user->subscription('default')->decrementQuantity(5);
```

你也可以使用 `updateQuantity` 方法设置具体数量：

```php
$user->subscription('default')->updateQuantity(10);
```

使用 `noProrate` 方法可以在更新订阅数量时不按比例分摊费用：

```php
$user->subscription('default')->noProrate()->updateQuantity(10);
```

有关订阅数量的更多信息，请参阅 [Stripe 文档](https://stripe.com/docs/subscriptions/quantities)。

<a name="quantities-for-subscription-with-multiple-products"></a>
#### 多产品订阅的数量

如果是 [多产品订阅](#subscriptions-with-multiple-products)，应将需要调整数量的价格 ID，作为第二个参数传给增加或减少数量的方法：

```php
$user->subscription('default')->incrementQuantity(1, 'price_chat');
```

<a name="subscriptions-with-multiple-products"></a>
### 多产品订阅

[多产品订阅](https://stripe.com/docs/billing/subscriptions/multiple-products) 允许你将多个计费产品分配给同一个订阅。例如，假设你正在构建客户服务「帮助台」应用，基础订阅价格为每月 10 美元，同时提供每月额外 15 美元的实时聊天附加产品。多产品订阅的信息存储在 Cashier 的 `subscription_items` 数据表中。

将价格数组作为第二个参数传给 `newSubscription` 方法，即可为订阅指定多个产品：

```php
use Illuminate\Http\Request;

Route::post('/user/subscribe', function (Request $request) {
    $request->user()->newSubscription('default', [
        'price_monthly',
        'price_chat',
    ])->create($request->paymentMethodId);

    // ...
});
```

上例会为客户的 `default` 订阅附加两个价格，分别按各自的计费周期收费。必要时，可以使用 `quantity` 方法为每个价格指定数量：

```php
$user = User::find(1);

$user->newSubscription('default', ['price_monthly', 'price_chat'])
    ->quantity(5, 'price_chat')
    ->create($paymentMethod);
```

如果希望向现有订阅添加另一个价格，可以调用订阅的 `addPrice` 方法：

```php
$user = User::find(1);

$user->subscription('default')->addPrice('price_chat');
```

上例会添加新价格，并在下一个计费周期向客户收费。如果希望立即收费，可以使用 `addPriceAndInvoice` 方法：

```php
$user->subscription('default')->addPriceAndInvoice('price_chat');
```

如果希望按指定数量添加价格，可以将数量作为第二个参数传给 `addPrice` 或 `addPriceAndInvoice` 方法：

```php
$user = User::find(1);

$user->subscription('default')->addPrice('price_chat', 5);
```

可以使用 `removePrice` 方法从订阅中移除价格：

```php
$user->subscription('default')->removePrice('price_chat');
```

> [!WARNING]
> 不能移除订阅中的最后一个价格。此时应直接取消订阅。

<a name="swapping-prices"></a>
#### 切换价格

你也可以更改多产品订阅附加的价格。例如，客户有一个包含 `price_chat` 附加产品的 `price_basic` 订阅，而你希望将客户从 `price_basic` 升级到 `price_pro`：

```php
use App\Models\User;

$user = User::find(1);

$user->subscription('default')->swap(['price_pro', 'price_chat']);
```

执行上例时，底层的 `price_basic` 订阅项会被删除，`price_chat` 订阅项会保留，并会创建新的 `price_pro` 订阅项。

你还可以向 `swap` 方法传入键值对数组，指定订阅项选项。例如，指定各订阅价格的数量：

```php
$user = User::find(1);

$user->subscription('default')->swap([
    'price_pro' => ['quantity' => 5],
    'price_chat'
]);
```

如果只希望切换订阅中的某个价格，可以在该订阅项本身上调用 `swap` 方法。当你希望保留订阅中其他价格的所有现有元数据时，这种方式尤其有用：

```php
$user = User::find(1);

$user->subscription('default')
    ->findItemOrFail('price_basic')
    ->swap('price_pro');
```

<a name="proration"></a>
#### 按比例分摊

默认情况下，在多产品订阅中添加或移除价格时，Stripe 会按比例分摊费用。如果希望调整价格时不进行费用分摊，应在价格操作中链式调用 `noProrate` 方法：

```php
$user->subscription('default')->noProrate()->removePrice('price_chat');
```

<a name="swapping-quantities"></a>
#### 数量

如果希望更新某个订阅价格的数量，可以使用 [现有的数量方法](#subscription-quantity)，并将价格 ID 作为额外参数传入：

```php
$user = User::find(1);

$user->subscription('default')->incrementQuantity(5, 'price_chat');

$user->subscription('default')->decrementQuantity(3, 'price_chat');

$user->subscription('default')->updateQuantity(10, 'price_chat');
```

> [!WARNING]
> 订阅包含多个价格时，`Subscription` 模型上的 `stripe_price` 和 `quantity` 属性为 `null`。要访问各个价格的属性，应使用 `Subscription` 模型上的 `items` 关系。

<a name="subscription-items"></a>
#### 订阅项

订阅包含多个价格时，数据库的 `subscription_items` 表中会存储多个订阅「项」。你可以通过订阅上的 `items` 关系访问它们：

```php
use App\Models\User;

$user = User::find(1);

$subscriptionItem = $user->subscription('default')->items->first();

// 获取指定订阅项的 Stripe 价格和数量……
$stripePrice = $subscriptionItem->stripe_price;
$quantity = $subscriptionItem->quantity;
```

你也可以使用 `findItemOrFail` 方法获取指定价格对应的订阅项：

```php
$user = User::find(1);

$subscriptionItem = $user->subscription('default')->findItemOrFail('price_chat');
```

<a name="multiple-subscriptions"></a>
### 多个订阅

Stripe 允许客户同时拥有多个订阅。例如，你经营一家健身房，提供游泳订阅和举重订阅，各自采用不同的定价。客户应能订阅其中一种或同时订阅两种方案。

应用创建订阅时，可以向 `newSubscription` 方法提供订阅类型。类型可以是任意字符串，用于表示用户正在创建的订阅种类：

```php
use Illuminate\Http\Request;

Route::post('/swimming/subscribe', function (Request $request) {
    $request->user()->newSubscription('swimming')
        ->price('price_swimming_monthly')
        ->create($request->paymentMethodId);

    // ...
});
```

上例为客户创建了月付游泳订阅，但客户之后可能希望改为年付。调整客户订阅时，只需切换 `swimming` 订阅上的价格：

```php
$user->subscription('swimming')->swap('price_swimming_yearly');
```

当然，你也可以完全取消订阅：

```php
$user->subscription('swimming')->cancel();
```

<a name="usage-based-billing"></a>
### 按用量计费

[按用量计费](https://stripe.com/docs/billing/subscriptions/metered-billing) 允许你根据客户在计费周期内的产品用量收费。例如，按客户每月发送的短信或电子邮件数量计费。

要开始按用量计费，首先在 Stripe 控制面板中创建新产品，使用 [按用量计费模型](https://docs.stripe.com/billing/subscriptions/usage-based/implementation-guide) 和 [计量器](https://docs.stripe.com/billing/subscriptions/usage-based/recording-usage#configure-meter)。创建计量器后，请保存其关联的事件名称和计量器 ID，以便上报和获取用量。然后，使用 `meteredPrice` 方法将计量价格 ID 添加到客户订阅中：

```php
use Illuminate\Http\Request;

Route::post('/user/subscribe', function (Request $request) {
    $request->user()->newSubscription('default')
        ->meteredPrice('price_metered')
        ->create($request->paymentMethodId);

    // ...
});
```

你也可以通过 [Stripe Checkout](#checkout) 创建按用量计费的订阅：

```php
$checkout = Auth::user()
    ->newSubscription('default', [])
    ->meteredPrice('price_metered')
    ->checkout();

return view('your-checkout-view', [
    'checkout' => $checkout,
]);
```

<a name="reporting-usage"></a>
#### 上报用量

客户使用应用时，你需要向 Stripe 上报其用量，以便准确计费。可以使用 `Billable` 模型上的 `reportMeterEvent` 方法上报计量事件的用量：

```php
$user = User::find(1);

$user->reportMeterEvent('emails-sent');
```

默认情况下，会向该计费周期增加 1 个单位的「用量」。你也可以传入具体用量，将其添加到客户在该计费周期的用量中：

```php
$user = User::find(1);

$user->reportMeterEvent('emails-sent', quantity: 15);
```

要获取客户在某个计量器下的事件摘要，可以使用 `Billable` 实例的 `meterEventSummaries` 方法：

```php
$user = User::find(1);

$meterUsage = $user->meterEventSummaries($meterId);

$meterUsage->first()->aggregated_value; // 10
```

有关计量事件摘要的更多信息，请参阅 Stripe 的 [Meter Event Summary 对象文档](https://docs.stripe.com/api/billing/meter-event_summary/object)。

要 [列出所有计量器](https://docs.stripe.com/api/billing/meter/list)，可以使用 `Billable` 实例的 `meters` 方法：

```php
$user = User::find(1);

$user->meters();
```

<a name="subscription-taxes"></a>
### 订阅税费

> [!WARNING]
> 你可以 [使用 Stripe Tax 自动计算税费](#tax-configuration)，无需手动计算税率。

要指定用户订阅适用的税率，应在可计费模型上实现 `taxRates` 方法，返回包含 Stripe 税率 ID 的数组。你可以在 [Stripe 控制面板](https://dashboard.stripe.com/test/tax-rates) 中定义这些税率：

```php
/**
 * 应用于客户订阅的税率。
 *
 * @return array<int, string>
 */
public function taxRates(): array
{
    return ['txr_id'];
}
```

`taxRates` 方法允许你为不同客户应用不同税率，适用于用户分布在多个国家、适用多种税率的情况。

如果提供多产品订阅，可以在可计费模型上实现 `priceTaxRates` 方法，为每个价格定义不同税率：

```php
/**
 * 应用于客户订阅的税率。
 *
 * @return array<string, array<int, string>>
 */
public function priceTaxRates(): array
{
    return [
        'price_monthly' => ['txr_id'],
    ];
}
```

> [!WARNING]
> `taxRates` 方法仅适用于订阅收费。如果使用 Cashier 进行「一次性」收费，需要在收费时手动指定税率。

<a name="syncing-tax-rates"></a>
#### 同步税率

更改 `taxRates` 方法返回的硬编码税率 ID 后，用户现有订阅的税务设置不会改变。如果希望按新的 `taxRates` 值更新现有订阅，应在用户的订阅实例上调用 `syncTaxRates` 方法：

```php
$user->subscription('default')->syncTaxRates();
```

这也会同步多产品订阅中各订阅项的税率。如果应用提供多产品订阅，请确保可计费模型实现了 [上文介绍的](#subscription-taxes) `priceTaxRates` 方法。

<a name="tax-exemption"></a>
#### 免税

Cashier 还提供 `isNotTaxExempt`、`isTaxExempt` 和 `reverseChargeApplies` 方法，用于判断客户是否免税。这些方法会调用 Stripe API 获取客户的免税状态：

```php
use App\Models\User;

$user = User::find(1);

$user->isTaxExempt();
$user->isNotTaxExempt();
$user->reverseChargeApplies();
```

> [!WARNING]
> 这些方法同样适用于任何 `Laravel\Cashier\Invoice` 对象。不过，在 `Invoice` 对象上调用时，它们判断的是发票创建时的免税状态。

<a name="subscription-anchor-date"></a>
### 订阅锚定日期

默认情况下，计费周期的锚点是订阅创建日期；如果设置了试用期，则是试用期结束日期。如果希望修改计费锚定日期，可以使用 `anchorBillingCycleOn` 方法：

```php
use Illuminate\Http\Request;

Route::post('/user/subscribe', function (Request $request) {
    $anchor = Carbon::parse('first day of next month');

    $request->user()->newSubscription('default', 'price_monthly')
        ->anchorBillingCycleOn($anchor->startOfDay())
        ->create($request->paymentMethodId);

    // ...
});
```

有关管理订阅计费周期的更多信息，请参阅 [Stripe 计费周期文档](https://stripe.com/docs/billing/subscriptions/billing-cycle)。

<a name="cancelling-subscriptions"></a>
### 取消订阅

要取消订阅，请在用户的订阅上调用 `cancel` 方法：

```php
$user->subscription('default')->cancel();
```

订阅取消时，Cashier 会自动设置 `subscriptions` 数据表的 `ends_at` 列。该列用于判断 `subscribed` 方法应从何时开始返回 `false`。

例如，客户在 3 月 1 日取消了原定于 3 月 5 日结束的订阅，那么 `subscribed` 方法会一直返回 `true`，直到 3 月 5 日。这是因为通常会允许用户继续使用应用，直到其计费周期结束。

可以使用 `onGracePeriod` 方法，判断用户是否已取消订阅但仍处于「宽限期」：

```php
if ($user->subscription('default')->onGracePeriod()) {
    // ...
}
```

如果希望立即取消订阅，请在用户的订阅上调用 `cancelNow` 方法：

```php
$user->subscription('default')->cancelNow();
```

如果希望立即取消订阅，并为尚未开票的计量用量，以及新增或待处理的按比例分摊发票项开具发票，请调用用户订阅上的 `cancelNowAndInvoice` 方法：

```php
$user->subscription('default')->cancelNowAndInvoice();
```

你也可以选择在指定时刻取消订阅：

```php
$user->subscription('default')->cancelAt(
    now()->plus(days: 10)
);
```

最后，在删除关联的用户模型之前，应始终先取消用户的订阅：

```php
$user->subscription('default')->cancelNow();

$user->delete();
```

<a name="resuming-subscriptions"></a>
### 恢复订阅

如果客户已取消订阅，而你希望恢复它，可以在订阅上调用 `resume` 方法。只有客户仍处于「宽限期」内，才能恢复订阅：

```php
$user->subscription('default')->resume();
```

客户取消订阅后，如果在订阅完全到期前恢复订阅，不会立即被收费。订阅会重新激活，并继续按照原来的计费周期收费。

<a name="subscription-trials"></a>
## 订阅试用

<a name="with-payment-method-up-front"></a>
### 预先提供支付方式

如果希望为客户提供试用期，同时预先收集支付方式信息，应在创建订阅时使用 `trialDays` 方法：

```php
use Illuminate\Http\Request;

Route::post('/user/subscribe', function (Request $request) {
    $request->user()->newSubscription('default', 'price_monthly')
        ->trialDays(10)
        ->create($request->paymentMethodId);

    // ...
});
```

该方法会在数据库的订阅记录中设置试用结束日期，并指示 Stripe 在该日期之后才开始向客户收费。使用 `trialDays` 方法时，Cashier 会覆盖 Stripe 中为该价格配置的默认试用期。

> [!WARNING]
> 如果未在试用结束日期之前取消客户订阅，试用期一结束就会向客户收费，因此务必告知用户试用结束日期。

`trialUntil` 方法允许你传入 `DateTime` 实例，指定试用期的结束时间：

```php
use Illuminate\Support\Carbon;

$user->newSubscription('default', 'price_monthly')
    ->trialUntil(Carbon::now()->plus(days: 10))
    ->create($paymentMethod);
```

你可以通过用户实例或订阅实例的 `onTrial` 方法判断用户是否处于试用期。以下两个示例等效：

```php
if ($user->onTrial('default')) {
    // ...
}

if ($user->subscription('default')->onTrial()) {
    // ...
}
```

可以使用 `endTrial` 方法立即结束订阅试用期：

```php
$user->subscription('default')->endTrial();
```

要判断现有试用期是否已经结束，可以使用 `hasExpiredTrial` 方法：

```php
if ($user->hasExpiredTrial('default')) {
    // ...
}

if ($user->subscription('default')->hasExpiredTrial()) {
    // ...
}
```

<a name="defining-trial-days-in-stripe-cashier"></a>
#### 在 Stripe / Cashier 中定义试用天数

你可以在 Stripe 控制面板中定义价格对应的试用天数，也可以始终通过 Cashier 显式传入。如果选择在 Stripe 中定义试用天数，请注意：除非显式调用 `skipTrial()` 方法，否则所有新订阅都会获得试用期，包括曾经订阅过的客户再次创建的订阅。

<a name="without-payment-method-up-front"></a>
### 不预先提供支付方式

如果希望提供试用期，但不预先收集用户的支付方式信息，可以将用户记录的 `trial_ends_at` 列设为所需的试用结束日期。通常在用户注册时完成此操作：

```php
use App\Models\User;

$user = User::create([
    // ...
    'trial_ends_at' => now()->plus(days: 10),
]);
```

> [!WARNING]
> 请务必在可计费模型的类定义中，为 `trial_ends_at` 属性添加 [日期类型转换](/docs/{{version}}/eloquent-mutators#date-casting)。

Cashier 将此类试用称为「通用试用」，因为它不关联任何现有订阅。如果当前日期尚未超过 `trial_ends_at` 的值，可计费模型实例的 `onTrial` 方法会返回 `true`：

```php
if ($user->onTrial()) {
    // 用户正处于试用期……
}
```

准备好为用户创建实际订阅后，可以照常使用 `newSubscription` 方法：

```php
$user = User::find(1);

$user->newSubscription('default', 'price_monthly')->create($paymentMethod);
```

要获取用户的试用结束日期，可以使用 `trialEndsAt` 方法。用户处于试用期时，该方法返回 Carbon 日期实例，否则返回 `null`。如果希望获取非默认订阅的试用结束日期，还可以传入可选的订阅类型参数：

```php
if ($user->onTrial()) {
    $trialEndsAt = $user->trialEndsAt('main');
}
```

如果希望明确判断用户是否正处于「通用」试用期，且尚未创建实际订阅，可以使用 `onGenericTrial` 方法：

```php
if ($user->onGenericTrial()) {
    // 用户正处于「通用」试用期……
}
```

<a name="extending-trials"></a>
### 延长试用期

`extendTrial` 方法允许你在订阅创建后延长试用期。即使试用期已经结束，客户已开始为订阅付费，你仍可以为其延长试用。试用期间对应的费用会从客户的下一张发票中扣除：

```php
use App\Models\User;

$subscription = User::find(1)->subscription('default');

// 将试用结束时间设为从现在起 7 天后……
$subscription->extendTrial(
    now()->plus(days: 7)
);

// 在现有试用期基础上再增加 5 天……
$subscription->extendTrial(
    $subscription->trial_ends_at->plus(days: 5)
);
```

<a name="handling-stripe-webhooks"></a>
## 处理 Stripe Webhook

> [!NOTE]
> 本地开发时，可以使用 [Stripe CLI](https://stripe.com/docs/stripe-cli) 辅助测试 Webhook。

Stripe 可以通过 Webhook 通知应用各种事件。默认情况下，Cashier 服务提供者会自动注册一个指向 Cashier Webhook 控制器的路由，由该控制器处理所有传入的 Webhook 请求。

默认情况下，Cashier Webhook 控制器会自动处理因扣款失败次数过多而取消的订阅（依据你的 Stripe 设置）、客户更新和删除、订阅更新以及支付方式变更。你也可以扩展该控制器，处理所需的其他 Stripe Webhook 事件，下文将介绍这一点。

为确保应用能够处理 Stripe Webhook，请在 Stripe 控制面板中配置 Webhook URL。默认情况下，Cashier Webhook 控制器响应 `/stripe/webhook` 路径。应在 Stripe 控制面板中启用的全部 Webhook 事件如下：

- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `customer.updated`
- `customer.deleted`
- `payment_method.automatically_updated`
- `invoice.payment_action_required`
- `invoice.payment_succeeded`

为方便起见，Cashier 提供了 `cashier:webhook` Artisan 命令，可在 Stripe 中创建一个监听 Cashier 所需全部事件的 Webhook：

```shell
php artisan cashier:webhook
```

默认情况下，创建的 Webhook 会指向由 `APP_URL` 环境变量和 Cashier 自带的 `cashier.webhook` 路由确定的 URL。如果希望使用其他 URL，可以在执行命令时提供 `--url` 选项：

```shell
php artisan cashier:webhook --url "https://example.com/stripe/webhook"
```

创建的 Webhook 会使用与 Cashier 相同的 Stripe API 版本，该版本由已安装的 `stripe/stripe-php` 版本决定。如果希望使用其他 Stripe 版本，可以提供 `--api-version` 选项：

```shell
php artisan cashier:webhook --api-version="2019-12-03"
```

Webhook 创建后会立即启用。如果希望先创建、等准备好后再启用，可以在执行命令时提供 `--disabled` 选项：

```shell
php artisan cashier:webhook --disabled
```

> [!WARNING]
> 请务必使用 Cashier 自带的 [Webhook 签名验证](#verifying-webhook-signatures) 中间件保护传入的 Stripe Webhook 请求。

<a name="webhooks-csrf-protection"></a>
#### Webhook 与 CSRF 保护

Stripe Webhook 需要绕过 Laravel 的 [CSRF 保护](/docs/{{version}}/csrf)，因此应确保 Laravel 不会尝试验证传入 Stripe Webhook 的 CSRF 令牌。在应用的 `bootstrap/app.php` 文件中，将 `stripe/*` 排除在 CSRF 保护之外即可：

```php
->withMiddleware(function (Middleware $middleware): void {
    $middleware->preventRequestForgery(except: [
        'stripe/*',
    ]);
})
```

<a name="defining-webhook-event-handlers"></a>
### 定义 Webhook 事件处理器

Cashier 会自动处理因扣款失败而取消的订阅，以及其他常见 Stripe Webhook 事件。如果还希望处理额外的 Webhook 事件，可以监听 Cashier 分发的以下事件：

- `Laravel\Cashier\Events\WebhookReceived`
- `Laravel\Cashier\Events\WebhookHandled`

这两个事件都包含 Stripe Webhook 的完整载荷。例如，要处理 `invoice.payment_succeeded` Webhook，可以注册一个 [监听器](/docs/{{version}}/events#defining-listeners)：

```php
<?php

namespace App\Listeners;

use Laravel\Cashier\Events\WebhookReceived;

class StripeEventListener
{
    /**
     * 处理接收到的 Stripe Webhook。
     */
    public function handle(WebhookReceived $event): void
    {
        if ($event->payload['type'] === 'invoice.payment_succeeded') {
            // 处理传入的事件……
        }
    }
}
```

<a name="verifying-webhook-signatures"></a>
### 验证 Webhook 签名

为保护 Webhook，可以使用 [Stripe Webhook 签名](https://stripe.com/docs/webhooks/signatures)。Cashier 自带了验证传入 Stripe Webhook 请求是否有效的中间件，方便你直接使用。

要启用 Webhook 验证，请确保在应用的 `.env` 文件中设置了 `STRIPE_WEBHOOK_SECRET` 环境变量。Webhook 的 `secret` 可以从 Stripe 账户控制面板获取。

<a name="single-charges"></a>
## 单次收费

<a name="simple-charge"></a>
### 简单收费

如果希望通过支付方式标识符向客户进行一次性收费，可以使用可计费模型实例上的 `charge` 方法。如果需要先收集客户的支付信息，再处理一次性收费，请参阅 [用于单次收费的 Payment Element](#payment-element-for-single-charges) 文档：

```php
use Illuminate\Http\Request;

Route::post('/purchase', function (Request $request) {
    $payment = $request->user()->charge(
        100, $request->paymentMethodId
    );

    // ...
});
```

`charge` 方法接收数组作为第三个参数，让你向底层创建 Stripe Payment Intent 的操作传入选项。有关创建 Payment Intent 时可用的选项，请参阅 [Stripe 文档](https://stripe.com/docs/api/payment_intents/create)：

```php
$user->charge(100, $paymentMethod, [
    'custom_option' => $value,
]);
```

你也可以在没有关联客户或用户的情况下使用 `charge` 方法。只需在应用可计费模型的新实例上调用它：

```php
use App\Models\User;

$payment = (new User)->charge(100, $paymentMethod);
```

收费失败时，`charge` 方法会抛出异常；收费成功时，则返回 `Laravel\Cashier\Payment` 实例：

```php
try {
    $payment = $user->charge(100, $paymentMethod);
} catch (Exception $e) {
    // ...
}
```

> [!WARNING]
> `charge` 方法接收的支付金额应以应用所用货币的最小单位表示。例如，客户使用美元支付时，金额应以美分为单位。

<a name="charge-with-invoice"></a>
### 开具发票并收费

有时，你需要进行一次性收费，并向客户提供 PDF 发票。`invoicePrice` 方法可实现这一点。例如，为客户购买的五件新衬衫开具发票：

```php
$user->invoicePrice('price_tshirt', 5);
```

该发票会立即通过用户的默认支付方式扣款。`invoicePrice` 方法还接收数组作为第三个参数，其中包含发票项的计费选项。第四个参数也是数组，用于指定发票本身的计费选项：

```php
$user->invoicePrice('price_tshirt', 5, [
    'discounts' => [
        ['coupon' => 'SUMMER21SALE']
    ],
], [
    'default_tax_rates' => ['txr_id'],
]);
```

与 `invoicePrice` 类似，你可以使用 `tabPrice` 方法将多个项目加入客户的「待结账单」，再为客户开具发票，从而合并进行一次性收费，每张发票最多支持 250 个项目。例如，为客户的五件衬衫和两个杯子开具发票：

```php
$user->tabPrice('price_tshirt', 5);
$user->tabPrice('price_mug', 2);
$user->invoice();
```

你也可以使用 `invoiceFor` 方法，通过客户的默认支付方式进行「一次性」收费：

```php
$user->invoiceFor('One Time Fee', 500);
```

虽然可以使用 `invoiceFor` 方法，但建议搭配预定义价格使用 `invoicePrice` 和 `tabPrice` 方法。这样，你可以在 Stripe 控制面板中获得更完善的产品销售分析和数据。

> [!WARNING]
> `invoice`、`invoicePrice` 和 `invoiceFor` 方法会创建 Stripe 发票，并在扣款失败时重试。如果不希望发票重试失败的扣款，需要在第一次扣款失败后通过 Stripe API 关闭发票。

<a name="creating-payment-intents"></a>
### 创建支付意向

在可计费模型实例上调用 `pay` 方法，可以创建新的 Stripe 支付意向。该方法创建的支付意向会被封装在 `Laravel\Cashier\Payment` 实例中：

```php
use Illuminate\Http\Request;

Route::post('/pay', function (Request $request) {
    $payment = $request->user()->pay(
        $request->get('amount')
    );

    return $payment->client_secret;
});
```

创建支付意向后，可以将客户端密钥返回给应用前端，让用户在浏览器中完成支付。有关使用 Stripe 支付意向构建完整支付流程的更多信息，请参阅 [Stripe 文档](https://stripe.com/docs/payments/accept-a-payment?platform=web)。

使用 `pay` 方法时，客户可以使用 Stripe 控制面板中启用的默认支付方式。如果只希望允许某些特定支付方式，可以使用 `payWith` 方法：

```php
use Illuminate\Http\Request;

Route::post('/pay', function (Request $request) {
    $payment = $request->user()->payWith(
        $request->get('amount'), ['card', 'bancontact']
    );

    return $payment->client_secret;
});
```

> [!WARNING]
> `pay` 和 `payWith` 方法接收的支付金额应以应用所用货币的最小单位表示。例如，客户使用美元支付时，金额应以美分为单位。

<a name="refunding-charges"></a>
### 退款

如果需要为 Stripe 支付退款，可以使用 `refund` 方法。该方法的第一个参数是 Stripe Payment Intent ID：

```php
$payment = $user->charge(100, $paymentMethodId);

$user->refund($payment->id);
```

<a name="invoices"></a>
## 发票

<a name="retrieving-invoices"></a>
### 获取发票

使用 `invoices` 方法可以方便地获取可计费模型的发票。该方法返回由 `Laravel\Cashier\Invoice` 实例组成的集合：

```php
$invoices = $user->invoices();
```

如果希望结果包含待处理发票，可以使用 `invoicesIncludingPending` 方法：

```php
$invoices = $user->invoicesIncludingPending();
```

可以使用 `findInvoice` 方法，通过 ID 获取指定发票：

```php
$invoice = $user->findInvoice($invoiceId);
```

<a name="displaying-invoice-information"></a>
#### 显示发票信息

为客户列出发票时，可以使用发票对象的方法显示相关信息。例如，在表格中列出每张发票，让用户方便地下载其中任意一张：

```blade
<table>
    @foreach ($invoices as $invoice)
        <tr>
            <td>{{ $invoice->date()->toFormattedDateString() }}</td>
            <td>{{ $invoice->total() }}</td>
            <td><a href="/user/invoice/{{ $invoice->id }}">Download</a></td>
        </tr>
    @endforeach
</table>
```

<a name="upcoming-invoices"></a>
### 下一张发票

要获取客户即将生成的下一张发票，可以使用 `upcomingInvoice` 方法：

```php
$invoice = $user->upcomingInvoice();
```

同样，如果客户有多个订阅，也可以获取某个订阅即将生成的下一张发票：

```php
$invoice = $user->subscription('default')->upcomingInvoice();
```

<a name="previewing-subscription-invoices"></a>
### 预览订阅发票

使用 `previewInvoice` 方法，可以在更改价格之前预览发票，了解某项价格变更将如何影响客户发票：

```php
$invoice = $user->subscription('default')->previewInvoice('price_yearly');
```

你可以向 `previewInvoice` 方法传入价格数组，预览包含多个新价格的发票：

```php
$invoice = $user->subscription('default')->previewInvoice(['price_yearly', 'price_metered']);
```

<a name="generating-invoice-pdfs"></a>
### 生成发票 PDF

生成发票 PDF 前，应使用 Composer 安装 Dompdf 库，它是 Cashier 默认的发票渲染器：

```shell
composer require dompdf/dompdf
```

在路由或控制器中，可以使用 `downloadInvoice` 方法生成指定发票的 PDF 下载。该方法会自动生成下载发票所需的 HTTP 响应：

```php
use Illuminate\Http\Request;

Route::get('/user/invoice/{invoice}', function (Request $request, string $invoiceId) {
    return $request->user()->downloadInvoice($invoiceId);
});
```

默认情况下，发票的所有数据均来自 Stripe 中存储的客户和发票信息，文件名根据 `app.name` 配置值生成。你也可以向 `downloadInvoice` 方法传入数组作为第二个参数，自定义部分数据，例如公司和产品详情：

```php
return $request->user()->downloadInvoice($invoiceId, [
    'vendor' => 'Your Company',
    'product' => 'Your Product',
    'street' => 'Main Str. 1',
    'location' => '2000 Antwerp, Belgium',
    'phone' => '+32 499 00 00 00',
    'email' => 'info@example.com',
    'url' => 'https://example.com',
    'vendorVat' => 'BE123456789',
]);
```

`downloadInvoice` 方法还允许通过第三个参数自定义文件名，并自动添加 `.pdf` 后缀：

```php
return $request->user()->downloadInvoice($invoiceId, [], 'my-invoice');
```

<a name="custom-invoice-render"></a>
#### 自定义发票渲染器

Cashier 也支持自定义发票渲染器。默认使用的 `DompdfInvoiceRenderer` 实现通过 [dompdf](https://github.com/dompdf/dompdf) PHP 库生成发票。你可以实现 `Laravel\Cashier\Contracts\InvoiceRenderer` 接口，使用其他渲染器。例如，通过调用第三方 PDF 渲染服务的 API 来生成发票 PDF：

```php
use Illuminate\Support\Facades\Http;
use Laravel\Cashier\Contracts\InvoiceRenderer;
use Laravel\Cashier\Invoice;

class ApiInvoiceRenderer implements InvoiceRenderer
{
    /**
     * 渲染给定发票，并返回原始 PDF 字节数据。
     */
    public function render(Invoice $invoice, array $data = [], array $options = []): string
    {
        $html = $invoice->view($data)->render();

        return Http::get('https://example.com/html-to-pdf', ['html' => $html])->get()->body();
    }
}
```

实现发票渲染器接口后，应更新应用的 `config/cashier.php` 文件中的 `cashier.invoices.renderer` 配置，将其设为自定义渲染器实现的类名。

<a name="checkout"></a>
## 结账

Cashier Stripe 也支持 [Stripe Checkout](https://stripe.com/payments/checkout)。Stripe Checkout 提供预构建的托管支付页面，免去自行实现收款页面的麻烦。

下文介绍如何开始搭配 Cashier 使用 Stripe Checkout。要进一步了解 Stripe Checkout，还可以阅读 [Stripe 的 Checkout 文档](https://stripe.com/docs/payments/checkout)。

<a name="product-checkouts"></a>
### 产品结账

在可计费模型上调用 `checkout` 方法，可以为 Stripe 控制面板中已有的产品发起结账。该方法会创建新的 Stripe Checkout 会话，默认需要传入 Stripe 价格 ID：

```php
use Illuminate\Http\Request;

Route::get('/product-checkout', function (Request $request) {
    return $request->user()->checkout('price_tshirt');
});
```

如有需要，也可以指定产品数量：

```php
use Illuminate\Http\Request;

Route::get('/product-checkout', function (Request $request) {
    return $request->user()->checkout(['price_tshirt' => 15]);
});
```

客户访问此路由时，会被重定向到 Stripe Checkout 页面。默认情况下，用户完成或取消购买后会返回应用的 `home` 路由。你也可以通过 `success_url` 和 `cancel_url` 选项指定自定义回调 URL：

```php
use Illuminate\Http\Request;

Route::get('/product-checkout', function (Request $request) {
    return $request->user()->checkout(['price_tshirt' => 1], [
        'success_url' => route('your-success-route'),
        'cancel_url' => route('your-cancel-route'),
    ]);
});
```

定义 `success_url` 结账选项时，可以让 Stripe 在访问该 URL 时，将结账会话 ID 作为查询字符串参数附加。只需在 `success_url` 的查询字符串中添加字面字符串 `{CHECKOUT_SESSION_ID}`，Stripe 就会将其替换为实际的结账会话 ID：

```php
use Illuminate\Http\Request;
use Stripe\Checkout\Session;
use Stripe\Customer;

Route::get('/product-checkout', function (Request $request) {
    return $request->user()->checkout(['price_tshirt' => 1], [
        'success_url' => route('checkout-success').'?session_id={CHECKOUT_SESSION_ID}',
        'cancel_url' => route('checkout-cancel'),
    ]);
});

Route::get('/checkout-success', function (Request $request) {
    $checkoutSession = $request->user()->stripe()->checkout->sessions->retrieve($request->get('session_id'));

    return view('checkout.success', ['checkoutSession' => $checkoutSession]);
})->name('checkout-success');
```

<a name="checkout-promotion-codes"></a>
#### 促销码

默认情况下，Stripe Checkout 不允许使用 [客户可兑换的促销码](https://stripe.com/docs/billing/subscriptions/discounts/codes)。调用 `allowPromotionCodes` 方法，即可为结账页面启用促销码：

```php
use Illuminate\Http\Request;

Route::get('/product-checkout', function (Request $request) {
    return $request->user()
        ->allowPromotionCodes()
        ->checkout('price_tshirt');
});
```

<a name="single-charge-checkouts"></a>
### 单次收费结账

对于尚未在 Stripe 控制面板中创建的临时产品，你也可以进行简单收费。在可计费模型上调用 `checkoutCharge` 方法，传入收费金额、产品名称及可选数量即可。客户访问此路由时，会被重定向到 Stripe Checkout 页面：

```php
use Illuminate\Http\Request;

Route::get('/charge-checkout', function (Request $request) {
    return $request->user()->checkoutCharge(1200, 'T-Shirt', 5);
});
```

> [!WARNING]
> 使用 `checkoutCharge` 方法时，Stripe 每次都会在控制面板中创建新的产品和价格。因此，建议预先在 Stripe 控制面板中创建产品，并改用 `checkout` 方法。

<a name="subscription-checkouts"></a>
### 订阅结账

> [!WARNING]
> 使用 Stripe Checkout 创建订阅时，需要在 Stripe 控制面板中启用 `customer.subscription.created` Webhook。该 Webhook 会在数据库中创建订阅记录，并存储所有相关订阅项。

你也可以使用 Stripe Checkout 创建订阅。通过 Cashier 的订阅构建器方法定义订阅后，调用 `checkout` 方法即可。客户访问此路由时，会被重定向到 Stripe Checkout 页面：

```php
use Illuminate\Http\Request;

Route::get('/subscription-checkout', function (Request $request) {
    return $request->user()
        ->newSubscription('default', 'price_monthly')
        ->checkout();
});
```

与产品结账一样，你可以自定义成功和取消 URL：

```php
use Illuminate\Http\Request;

Route::get('/subscription-checkout', function (Request $request) {
    return $request->user()
        ->newSubscription('default', 'price_monthly')
        ->checkout([
            'success_url' => route('your-success-route'),
            'cancel_url' => route('your-cancel-route'),
        ]);
});
```

当然，也可以为订阅结账启用促销码：

```php
use Illuminate\Http\Request;

Route::get('/subscription-checkout', function (Request $request) {
    return $request->user()
        ->newSubscription('default', 'price_monthly')
        ->allowPromotionCodes()
        ->checkout();
});
```

> [!WARNING]
> Stripe Checkout 创建订阅时，并不支持所有订阅计费选项。在订阅构建器上使用 `anchorBillingCycleOn` 方法、设置按比例分摊行为或支付行为，都不会影响 Stripe Checkout 会话。请参阅 [Stripe Checkout Session API 文档](https://stripe.com/docs/api/checkout/sessions/create)，了解可用参数。

<a name="stripe-checkout-trial-periods"></a>
#### Stripe Checkout 与试用期

构建将通过 Stripe Checkout 完成的订阅时，你可以定义试用期：

```php
$checkout = Auth::user()->newSubscription('default', 'price_monthly')
    ->trialDays(3)
    ->checkout();
```

不过，试用期必须至少为 48 小时，这是 Stripe Checkout 支持的最短试用时间。

<a name="stripe-checkout-subscriptions-and-webhooks"></a>
#### 订阅与 Webhook

请记住，Stripe 和 Cashier 通过 Webhook 更新订阅状态，因此客户填写支付信息并返回应用时，订阅可能尚未生效。对于这种情况，你可以显示提示，告知用户支付或订阅正在等待处理。

<a name="collecting-tax-ids"></a>
### 收集税号

Checkout 也支持收集客户税号。要在结账会话中启用此功能，请在创建会话时调用 `collectTaxIds` 方法：

```php
$checkout = $user->collectTaxIds()->checkout('price_tshirt');
```

调用此方法后，客户会看到一个新的复选框，用于表明是否以公司名义购买。如果是，就可以提供税号。

> [!WARNING]
> 如果已在应用的服务提供者中配置 [自动税费计算](#tax-configuration)，此功能会自动启用，无需调用 `collectTaxIds` 方法。

<a name="guest-checkouts"></a>
### 游客结账

使用 `Checkout::guest` 方法，可以为应用中没有「账户」的游客创建结账会话：

```php
use Illuminate\Http\Request;
use Laravel\Cashier\Checkout;

Route::get('/product-checkout', function (Request $request) {
    return Checkout::guest()->create('price_tshirt', [
        'success_url' => route('your-success-route'),
        'cancel_url' => route('your-cancel-route'),
    ]);
});
```

与为现有用户创建结账会话一样，你可以使用 `Laravel\Cashier\CheckoutBuilder` 实例上的其他方法，自定义游客结账会话：

```php
use Illuminate\Http\Request;
use Laravel\Cashier\Checkout;

Route::get('/product-checkout', function (Request $request) {
    return Checkout::guest()
        ->withPromotionCode('promo-code')
        ->create('price_tshirt', [
            'success_url' => route('your-success-route'),
            'cancel_url' => route('your-cancel-route'),
        ]);
});
```

游客结账完成后，Stripe 可以分发 `checkout.session.completed` Webhook 事件，因此请确保已 [配置 Stripe Webhook](https://dashboard.stripe.com/webhooks)，将该事件发送到应用。在 Stripe 控制面板中启用后，即可 [通过 Cashier 处理该 Webhook](#handling-stripe-webhooks)。Webhook 载荷中包含的是 [Checkout 对象](https://stripe.com/docs/api/checkout/sessions/object)，你可以检查该对象，以履行客户订单。

<a name="handling-failed-payments"></a>
## 处理支付失败

订阅或单次收费的支付有时会失败。此时，Cashier 会抛出 `Laravel\Cashier\Exceptions\IncompletePayment` 异常。捕获该异常后，你有两种后续处理方式。

第一种方式是将客户重定向到 Cashier 自带的支付确认页面。Cashier 服务提供者已为此页面注册命名路由，因此可以捕获 `IncompletePayment` 异常后，将用户重定向到该页面：

```php
use Laravel\Cashier\Exceptions\IncompletePayment;

try {
    $subscription = $user->newSubscription('default', 'price_monthly')
        ->create($paymentMethod);
} catch (IncompletePayment $exception) {
    return redirect()->route(
        'cashier.payment',
        [$exception->payment->id, 'redirect' => route('home')]
    );
}
```

在支付确认页面，客户需要重新输入信用卡信息，并完成 Stripe 要求的额外操作，例如「3D Secure」验证。确认支付后，用户会被重定向到上述 `redirect` 参数指定的 URL，且 URL 会附加 `message`（字符串）和 `success`（整数）查询参数。支付页面目前支持以下支付方式：

<div class="content-list" markdown="1">

- 信用卡
- 支付宝
- Bancontact
- BECS 直接借记
- EPS
- Giropay
- iDEAL
- SEPA 直接借记

</div>

另一种方式是让 Stripe 处理支付确认。你可以在 Stripe 控制面板中 [设置自动账单邮件](https://dashboard.stripe.com/account/billing/automatic)，而不将用户重定向到支付确认页面。不过，捕获到 `IncompletePayment` 异常后，仍应告知用户将收到包含后续支付确认指引的邮件。

使用 `Billable` trait 的模型，其 `charge`、`invoiceFor` 和 `invoice` 方法可能抛出支付异常。操作订阅时，`SubscriptionBuilder` 的 `create` 方法，以及 `Subscription` 和 `SubscriptionItem` 模型的 `incrementAndInvoice`、`swapAndInvoice` 方法，也可能抛出未完成支付异常。

可以在可计费模型或订阅实例上使用 `hasIncompletePayment` 方法，判断现有订阅是否存在未完成支付：

```php
if ($user->hasIncompletePayment('default')) {
    // ...
}

if ($user->subscription('default')->hasIncompletePayment()) {
    // ...
}
```

检查异常实例的 `payment` 属性，可以获取未完成支付的具体状态：

```php
use Laravel\Cashier\Exceptions\IncompletePayment;

try {
    $user->charge(1000, 'pm_card_threeDSecure2Required');
} catch (IncompletePayment $exception) {
    // 获取支付意向的状态……
    $exception->payment->status;

    // 检查特定条件……
    if ($exception->payment->requiresPaymentMethod()) {
        // ...
    } elseif ($exception->payment->requiresConfirmation()) {
        // ...
    }
}
```

<a name="confirming-payments"></a>
### 确认支付

某些支付方式在确认支付时需要额外数据。例如，SEPA 支付方式需要额外的「授权委托」数据。你可以使用 `withPaymentConfirmationOptions` 方法将这些数据传给 Cashier：

```php
$subscription->withPaymentConfirmationOptions([
    'mandate_data' => '...',
])->swap('price_xxx');
```

确认支付时支持的全部选项，请参阅 [Stripe API 文档](https://stripe.com/docs/api/payment_intents/confirm)。

<a name="strong-customer-authentication"></a>
## 强客户认证

如果你的业务或某位客户位于欧洲，就需要遵守欧盟的强客户认证（SCA）法规。欧盟于 2019 年 9 月实施这些规定，以防止支付欺诈。Stripe 和 Cashier 已提供构建符合 SCA 要求的应用所需的支持。

> [!WARNING]
> 开始之前，请阅读 [Stripe 关于 PSD2 和 SCA 的指南](https://stripe.com/guides/strong-customer-authentication)，以及 [新版 SCA API 文档](https://stripe.com/docs/strong-customer-authentication)。

<a name="payments-requiring-additional-confirmation"></a>
### 需要额外确认的支付

SCA 法规通常要求额外验证，才能确认并处理支付。此时，Cashier 会抛出 `Laravel\Cashier\Exceptions\IncompletePayment` 异常，表明需要进一步验证。有关处理这些异常的更多信息，请参阅 [处理支付失败](#handling-failed-payments) 文档。

Stripe 或 Cashier 提供的支付确认界面可能会针对特定银行或发卡机构的流程调整，包含额外的银行卡确认、临时小额扣款、独立设备认证或其他验证方式。

<a name="incomplete-and-past-due-state"></a>
#### 未完成和逾期状态

支付需要额外确认时，订阅会保持 `incomplete` 或 `past_due` 状态，并记录在数据库的 `stripe_status` 列中。支付确认完成，且 Stripe 通过 Webhook 通知应用后，Cashier 就会自动激活客户订阅。

有关 `incomplete` 和 `past_due` 状态的更多信息，请参阅 [这些状态的补充文档](#incomplete-and-past-due-status)。

<a name="off-session-payment-notifications"></a>
### 非会话支付通知

SCA 法规要求客户即使拥有有效订阅，也可能需要不定期验证支付信息。因此，当客户未参与支付会话时发起的支付需要确认（例如订阅续费）时，Cashier 可以向其发送通知。将 `CASHIER_PAYMENT_NOTIFICATION` 环境变量设为通知类，即可启用此功能。默认情况下不发送通知。Cashier 自带了可用于此目的的通知类，你也可以提供自己的通知类：

```ini
CASHIER_PAYMENT_NOTIFICATION=Laravel\Cashier\Notifications\ConfirmPayment
```

为确保非会话支付确认通知能够送达，请确认应用已 [配置 Stripe Webhook](#handling-stripe-webhooks)，并在 Stripe 控制面板中启用 `invoice.payment_action_required` Webhook。此外，`Billable` 模型还应使用 Laravel 的 `Illuminate\Notifications\Notifiable` trait。

> [!WARNING]
> 客户手动发起需要额外确认的支付时，同样会收到通知，因为 Stripe 无法区分支付是手动发起还是「非会话」发起的。不过，客户确认支付后再次访问支付页面，只会看到「支付成功」消息，不会因重复确认同一笔支付而意外被扣款两次。

<a name="stripe-sdk"></a>
## Stripe SDK

Cashier 的许多对象都封装了 Stripe SDK 对象。如果希望直接操作 Stripe 对象，可以通过 `asStripe` 方法获取：

```php
$stripeSubscription = $subscription->asStripeSubscription();

$stripeSubscription->application_fee_percent = 5;

$stripeSubscription->save();
```

你也可以使用 `updateStripeSubscription` 方法直接更新 Stripe 订阅：

```php
$subscription->updateStripeSubscription(['application_fee_percent' => 5]);
```

如果希望直接使用 `Stripe\StripeClient` 客户端，可以调用 `Cashier` 类的 `stripe` 方法。例如，获取 `StripeClient` 实例并查询 Stripe 账户中的价格列表：

```php
use Laravel\Cashier\Cashier;

$prices = Cashier::stripe()->prices->all();
```

<a name="testing"></a>
## 测试

测试使用 Cashier 的应用时，你可以模拟发送到 Stripe API 的实际 HTTP 请求，但这需要重新实现 Cashier 的部分行为。因此，建议让测试访问真实的 Stripe API。虽然速度较慢，但更能确认应用是否按预期工作；较慢的测试可以放入独立的 Pest / PHPUnit 测试分组。

测试时请记住，Cashier 本身已有完善的测试套件，因此应专注于应用自身的订阅和支付流程，无需测试 Cashier 的每项底层行为。

首先，将 Stripe 的 **测试环境** 密钥添加到 `phpunit.xml` 文件：

```xml
<env name="STRIPE_SECRET" value="sk_test_<your-key>"/>
```

现在，测试中与 Cashier 交互时，会向 Stripe 测试环境发送实际 API 请求。为方便测试，应预先在 Stripe 测试账户中创建测试所需的订阅和价格。

> [!NOTE]
> 要测试信用卡被拒绝、支付失败等多种计费场景，可以使用 Stripe 提供的各种 [测试卡号和令牌](https://stripe.com/docs/testing)。
