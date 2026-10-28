
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
    - [检索客户](#retrieving-customers)
    - [创建客户](#creating-customers)
    - [更新客户](#updating-customers)
    - [余额](#balances)
    - [税号](#tax-ids)
	- [使用 Stripe 同步客户数据](#syncing-customer-data-with-stripe)
    - [计费门户](#billing-portal)
- [支付方式](#payment-methods)
    - [存储支付方式](#storing-payment-methods)
    - [检索支付方式](#retrieving-payment-methods)
    - [当前支付方式](#payment-method-presence)
    - [更新默认支付方式](#updating-the-default-payment-method)
    - [添加支付方式](#adding-payment-methods)
    - [删除支付方式](#deleting-payment-methods)
- [订阅](#subscriptions)
    - [创建订阅](#creating-subscriptions)
    - [检查订阅状态](#checking-subscription-status)
    - [修改价格](#changing-prices)
    - [订阅数量](#subscription-quantity)
    - [多产品订阅](#subscriptions-with-multiple-products)
    - [多个订阅](#multiple-subscriptions)
    - [基于使用量的计费](#usage-based-billing)
    - [订阅税费](#subscription-taxes)
    - [订阅锚定日期](#subscription-anchor-date)
    - [取消订阅](#cancelling-subscriptions)
    - [续订订阅](#resuming-subscriptions)
- [订阅试用](#subscription-trials)
    - [预付支付方式](#with-payment-method-up-front)
    - [非预付支付方式](#without-payment-method-up-front)
    - [延长试用](#extending-trials)
- [处理 Stripe Webhooks](#handling-stripe-webhooks)
    - [定义 Webhook 事件处理器](#defining-webhook-event-handlers)
    - [验证 Webhook 签名](#verifying-webhook-signatures)
- [单次收费](#single-charges)
    - [简单收费](#simple-charge)
    - [使用发票收费](#charge-with-invoice)
    - [创建支付意向](#creating-payment-intents)
    - [退款费用](#refunding-charges)
- [结账](#checkout)
    - [产品结账](#product-checkouts)
    - [单次收费结账](#single-charge-checkouts)
    - [订阅结账](#subscription-checkouts)
    - [收集税号](#collecting-tax-ids)
    - [游客结账](#guest-checkouts)
- [发票](#invoices)
    - [检索发票](#retrieving-invoices)
    - [即将到期的发票](#upcoming-invoices)
    - [预览订阅发票](#previewing-subscription-invoices)
    - [生成发票 PDFs](#generating-invoice-pdfs)
- [处理支付失败](#handling-failed-payments)
    - [确认支付](#confirming-payments)
- [强客户认证 (SCA)](#strong-customer-authentication)
    - [支付额外确认](#payments-requiring-additional-confirmation)
    - [关闭会话支付通知](#off-session-payment-notifications)
- [Stripe SDK](#stripe-sdk)
- [测试](#testing)



## 介绍（Introduction）

[Laravel Cashier Stripe](https://github.com/laravel/cashier-stripe) 为 [Stripe](https://stripe.com) 的订阅计费服务提供了一个简洁且流畅的接口。
它处理了几乎所有让你头疼的订阅计费样板代码。除了基本的订阅管理之外，Cashier 还可以处理优惠券、订阅切换、订阅“数量”、取消宽限期，甚至还能生成发票 PDF。

## 升级 Cashier（Upgrading Cashier）

当你升级到新版本的 Cashier 时，请务必仔细阅读 [升级指南](https://github.com/laravel/cashier-stripe/blob/master/UPGRADE.md)。

> [!WARNING]
> 为了避免重大变更（Breaking Changes），Cashier 使用固定的 Stripe API 版本。
> Cashier 15 使用的 Stripe API 版本为 `2023-10-16`。
> Stripe API 版本将在次要版本更新（minor releases）时升级，以便使用新的 Stripe 功能和改进。

## 安装（Installation）

首先，使用 Composer 包管理器安装用于 Stripe 的 Cashier 包：

```shell
composer require laravel/cashier
```

安装完成后，通过 `vendor:publish` Artisan 命令发布 Cashier 的数据库迁移文件：

```shell
php artisan vendor:publish --tag="cashier-migrations"
```

Then, migrate your database:

```shell
php artisan migrate
```

Cashier 的迁移会在你的 `users` 表中添加若干列。
同时，它还会创建一个新的 `subscriptions` 表，用于存储所有客户的订阅信息，
以及一个 `subscription_items` 表，用于存储包含多个价格项的订阅。

如果你愿意，也可以通过以下命令发布 Cashier 的配置文件：

```shell
php artisan vendor:publish --tag="cashier-config"
```

最后，为了确保 Cashier 能正确处理所有 Stripe 事件，请记得[配置 Cashier 的 webhook 处理](#handling-stripe-webhooks)。

> [!警告]
> Stripe 建议所有用于存储 Stripe 标识符（如 `stripe_id`）的数据库列都应区分大小写。
> 因此，在使用 MySQL 时，应确保 `stripe_id` 列的排序规则（collation）设置为 `utf8_bin`。
> 有关更多信息，请参阅 [Stripe 官方文档](https://stripe.com/docs/upgrades#what-changes-does-stripe-consider-to-be-backwards-compatible)。



## 配置（Configuration）

### 可计费模型（Billable Model）

在使用 Cashier 之前，请在你的可计费模型定义中加入 `Billable` trait。
通常，这个模型是 `App\Models\User`。
该 trait 提供了多种方法，让你可以执行常见的计费任务，例如创建订阅、应用优惠券以及更新支付方式信息：

```php
use Laravel\Cashier\Billable;

class User extends Authenticatable
{
    use Billable;
}
```

Cashier 默认假设你的可计费模型是 Laravel 自带的 `App\Models\User` 类。
如果你希望更改这一点，可以通过 `useCustomerModel` 方法指定一个不同的模型。
通常，这个方法应在 `AppServiceProvider` 类的 `boot` 方法中调用：

```php
use App\Models\Cashier\User;
use Laravel\Cashier\Cashier;

/**
 * 启动任何应用服务。
 */
public function boot(): void
{
    Cashier::useCustomerModel(User::class);
}
```

> [!警告]
> 如果你使用的模型不是 Laravel 默认提供的 `App\Models\User` 模型，那么你需要发布并修改 [Cashier 的迁移文件](#installation)，以便与自定义模型的表名相匹配。

### API 密钥（API Keys）

接下来，你需要在应用的 `.env` 文件中配置 Stripe 的 API 密钥。
你可以在 Stripe 控制面板中获取这些密钥：

```ini
STRIPE_KEY=your-stripe-key
STRIPE_SECRET=your-stripe-secret
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
```

> [!警告]
> 请确保在应用的 `.env` 文件中定义了 `STRIPE_WEBHOOK_SECRET` 环境变量，因为该变量用于验证传入的 webhook 请求确实来自 Stripe。

### 货币配置（Currency Configuration）

Cashier 默认使用的货币是美元（USD）。
你可以在应用的 `.env` 文件中设置 `CASHIER_CURRENCY` 环境变量来更改默认货币：

```ini
CASHIER_CURRENCY=eur
```



除了配置 Cashier 的货币之外，你还可以指定用于在发票上显示货币数值时的 **本地化设置（locale）**。
在内部，Cashier 使用 [PHP 的 `NumberFormatter` 类](https://www.php.net/manual/en/class.numberformatter.php) 来设置货币的本地化格式：

```ini
CASHIER_CURRENCY_LOCALE=nl_BE
```

> [!警告]
> 如果要使用除 `en` 之外的其他语言环境，请确保服务器上已安装并配置 `ext-intl` PHP 扩展。

### 税务配置（Tax Configuration）

借助 [Stripe Tax](https://stripe.com/tax)，可以为 Stripe 生成的所有发票自动计算税额。
你可以在应用程序的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中调用 `calculateTaxes` 方法来启用自动税额计算：

```php
use Laravel\Cashier\Cashier;

/**
 * 启动应用程序服务。
 */
public function boot(): void
{
    Cashier::calculateTaxes();
}
```

启用税额计算后，任何新创建的订阅和一次性发票都将自动计算税额。

为了让此功能正常工作，你的客户账单信息（如客户姓名、地址和税号）需要与 Stripe 同步。
你可以使用 Cashier 提供的 [客户数据同步](#syncing-customer-data-with-stripe) 和 [税号（Tax ID）](#tax-ids) 方法来实现这一点。

### 日志记录（Logging）

Cashier 允许你指定在记录 Stripe 严重错误日志时所使用的日志通道。
你可以在应用程序的 `.env` 文件中定义 `CASHIER_LOGGER` 环境变量来设置日志通道：

```ini
CASHIER_LOGGER=stack
```

通过对 Stripe 的 API 调用而产生的异常将通过应用程序的默认日志通道进行记录。



### 使用自定义模型（Using Custom Models）

你可以通过定义自己的模型并继承 Cashier 对应的模型，来自由扩展 Cashier 内部使用的模型：

```php
use Laravel\Cashier\Subscription as CashierSubscription;

class Subscription extends CashierSubscription
{
    // ...
}
```

定义好自定义模型后，你可以通过 `Laravel\Cashier\Cashier` 类指示 Cashier 使用你的自定义模型。
通常，你应该在应用程序的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中告知 Cashier 使用这些自定义模型：

```php
use App\Models\Cashier\Subscription;
use App\Models\Cashier\SubscriptionItem;

/**
 * 启动应用程序服务。
 */
public function boot(): void
{
    Cashier::useSubscriptionModel(Subscription::class);
    Cashier::useSubscriptionItemModel(SubscriptionItem::class);
}
```

## 快速入门（Quickstart）

### 销售产品（Selling Products）

> [!注意]
> 在使用 Stripe Checkout 之前，你应当在 Stripe 控制台中定义具有固定价格的产品。
> 此外，你还应当[配置 Cashier 的 webhook 处理](#handling-stripe-webhooks)。

通过你的应用程序提供产品销售和订阅计费功能可能看起来很复杂。
然而，借助 Cashier 和 [Stripe Checkout](https://stripe.com/payments/checkout)，你可以轻松构建现代化且稳定的支付集成。

若要向客户收取一次性、非循环的产品费用，我们可以使用 Cashier 将客户引导至 Stripe Checkout 页面，让他们在其中填写支付信息并确认购买。
支付完成后，客户将被重定向到你在应用程序中指定的成功页面 URL：

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



正如上面的示例所示，我们将使用 Cashier 提供的 `checkout` 方法，将客户根据指定的 “价格标识符（price identifier）” 重定向到 Stripe Checkout。
在 Stripe 中，“价格（price）” 是指[为特定产品定义的价格](https://stripe.com/docs/products-prices/how-products-and-prices-work)。

如果有需要，`checkout` 方法会自动在 Stripe 中创建一个客户，并将该 Stripe 客户记录与应用程序数据库中的相应用户关联起来。
当结账会话完成后，客户会被重定向到一个专门的成功页面或取消页面，在那里你可以向客户显示相关的提示信息。

#### 向 Stripe Checkout 提供元数据（Providing Meta Data to Stripe Checkout）

在销售产品时，通常会通过你自己应用程序中定义的 `Cart`（购物车）和 `Order`（订单）模型来跟踪已完成的订单和已购买的商品。
当你将客户重定向到 Stripe Checkout 以完成购买时，可能需要提供一个现有的订单标识符，以便在客户返回你的应用程序时，将完成的购买与相应订单关联起来。

为此，你可以向 `checkout` 方法提供一个包含 `metadata`（元数据）的数组。
假设当用户开始结账流程时，你的应用程序会创建一个待处理的 `Order` 记录。
请注意，这里的 `Cart` 和 `Order` 模型只是示例说明，Cashier 并未提供这些模型。
你可以根据自己应用程序的需求自由实现这些概念：

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



正如上面的示例所示，当用户开始结账流程时，我们会将购物车或订单中所有关联的 Stripe 价格标识符传递给 `checkout` 方法。
当然，当客户将商品加入购物车或订单时，你的应用程序需要负责将这些商品与“购物车”或订单进行关联。
此外，我们还通过 `metadata` 数组将订单的 ID 提供给 Stripe Checkout 会话。
最后，我们在 Checkout 成功回调路由中添加了 `CHECKOUT_SESSION_ID` 模板变量。当 Stripe 将客户重定向回你的应用程序时，该模板变量会自动被填充为对应的 Checkout 会话 ID。

接下来，让我们构建 Checkout 成功回调路由。
这是当用户通过 Stripe Checkout 完成购买后将被重定向到的路由。
在该路由中，我们可以获取 Stripe Checkout 会话 ID，并通过它检索对应的 Stripe Checkout 实例，从而访问我们之前提供的元数据，并据此更新客户的订单状态：

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

有关 Checkout 会话对象中包含的数据的更多信息，请参阅 Stripe 的文档：[Checkout session 对象数据说明](https://stripe.com/docs/api/checkout/sessions/object)。


### 销售订阅（Selling Subscriptions）

> [!注意]
> 在使用 Stripe Checkout 之前，你应当在 Stripe 控制台中定义具有固定价格的产品。此外，你还应当[配置 Cashier 的 webhook 处理](#handling-stripe-webhooks)。

通过你的应用程序提供产品和订阅计费功能可能看起来很复杂。
然而，借助 Cashier 和 [Stripe Checkout](https://stripe.com/payments/checkout)，你可以轻松构建现代且稳定的支付集成。

为了学习如何使用 Cashier 和 Stripe Checkout 销售订阅，让我们来看一个简单的场景：
一个订阅服务提供基础月付计划（`price_basic_monthly`）和年付计划（`price_basic_yearly`）。
这两个价格可以在 Stripe 控制台中归类到一个名为 “Basic” 的产品（`pro_basic`）下。
此外，我们的订阅服务还可能提供一个名为 “Expert” 的高级计划（`pro_expert`）。

首先，让我们看看客户如何订阅我们的服务。
当然，你可以想象客户会在应用程序的定价页面上点击 “订阅” 按钮来选择 Basic 计划。
该按钮或链接应当引导用户访问一个 Laravel 路由，用于为他们选择的方案创建 Stripe Checkout 会话：

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

正如上面的示例所示，我们会将客户重定向到一个 Stripe Checkout 会话，让他们能够订阅我们的 Basic 计划。
在成功结账或取消之后，客户会被重定向回我们通过 `checkout` 方法提供的 URL。
为了了解他们的订阅何时真正开始（因为某些支付方式可能需要几秒钟来处理），我们还需要[配置 Cashier 的 webhook 处理](#handling-stripe-webhooks)。



现在客户已经可以开始订阅，我们需要限制应用程序的某些部分，使只有已订阅用户才能访问。
当然，我们可以通过 Cashier 的 `Billable` trait 提供的 `subscribed` 方法来确定用户当前的订阅状态：


```blade
@if ($user->subscribed())
    <p>You are subscribed.</p>
@endif
```

我们甚至可以轻松地判断用户是否订阅了特定的产品或价格方案：

```blade
@if ($user->subscribedToProduct('pro_basic'))
    <p>You are subscribed to our Basic product.</p>
@endif

@if ($user->subscribedToPrice('price_basic_monthly'))
    <p>You are subscribed to our monthly Basic plan.</p>
@endif
```

#### 构建 Subscribed 中间件

为了方便起见，您可能希望创建一个 [中间件](/docs/laravel/12.x/middleware)，用于判断传入的请求是否来自已订阅用户。
定义此中间件后，您可以轻松地将其分配给路由，从而防止未订阅用户访问该路由：

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
            // 将用户重定向到结算页面，并提示他们进行订阅...
            return redirect('/billing');
        }

        return $next($request);
    }
}
```

定义好中间件后，您可以将它分配给路由：

```php
use App\Http\Middleware\Subscribed;

Route::get('/dashboard', function () {
    // ...
})->middleware([Subscribed::class]);
```

#### 允许客户管理他们的订阅计划

当然，客户可能希望将他们的订阅计划更改为其他产品或“等级”。
最简单的方式是将客户引导至 Stripe 的 [客户结算门户 (Customer Billing Portal)](https://stripe.com/docs/no-code/customer-portal)，
该门户提供一个托管的用户界面，使客户能够下载发票、更新付款方式以及更改订阅计划。



首先，在应用程序中定义一个链接或按钮，指向一个 Laravel 路由，我们将利用该路由来启动一个结算门户（Billing Portal）会话：

```blade
<a href="{{ route('billing') }}">
    Billing
</a>
```

接下来，我们定义一个路由，用于启动一个 Stripe 客户结算门户（Customer Billing Portal）会话，并将用户重定向到该门户。
`redirectToBillingPortal` 方法接收一个 URL 参数，用于指定用户退出门户后应返回的页面地址：

```php
use Illuminate\Http\Request;

Route::get('/billing', function (Request $request) {
    return $request->user()->redirectToBillingPortal(route('dashboard'));
})->middleware(['auth'])->name('billing');
```

> [!注意]
> 只要您配置了 Cashier 的 webhook 处理功能，Cashier 就会自动通过检查来自 Stripe 的入站 webhook 来保持应用程序中与 Cashier 相关的数据库表同步。
例如，当用户通过 Stripe 的客户结算门户取消订阅时，Cashier 会接收到相应的 webhook，并在您的应用数据库中将该订阅标记为“已取消”。

## 客户（Customers）

### 获取客户

您可以使用 `Cashier::findBillable` 方法通过 Stripe ID 检索客户。
此方法将返回一个可计费（billable）模型的实例：

```php
use Laravel\Cashier\Cashier;

$user = Cashier::findBillable($stripeId);
```

### 创建客户

有时，您可能希望在未开始订阅的情况下创建一个 Stripe 客户。
您可以使用 `createAsStripeCustomer` 方法来实现：

```php
$stripeCustomer = $user->createAsStripeCustomer();
```

一旦客户已在 Stripe 中创建，您可以在之后的任意时间开始订阅。
此外，您可以传递一个可选的 `$options` 数组，用于传入任何 Stripe API 所支持的[客户创建参数](https://stripe.com/docs/api/customers/create)：

```php
$stripeCustomer = $user->createAsStripeCustomer($options);
```



如果您想为可计费（billable）模型返回对应的 Stripe 客户对象，可以使用 `asStripeCustomer` 方法：

```php
$stripeCustomer = $user->asStripeCustomer();
```

如果您想获取某个可计费模型的 Stripe 客户对象，但不确定该模型是否已经是 Stripe 中的客户，可以使用 `createOrGetStripeCustomer` 方法。
该方法会在 Stripe 中创建一个新客户（如果尚不存在的话）：

```php
$stripeCustomer = $user->createOrGetStripeCustomer();
```

### 更新客户

有时，您可能希望直接在 Stripe 中更新客户的附加信息。
可以使用 `updateStripeCustomer` 方法来实现。
该方法接收一个数组，包含 [Stripe API 支持的客户更新选项](https://stripe.com/docs/api/customers/update)：

```php
$stripeCustomer = $user->updateStripeCustomer($options);
```

### 余额（Balances）

Stripe 允许您为客户的“余额”进行充值（credit）或扣款（debit）。
之后，这个余额会在新的发票中进行抵扣或加收。
要检查客户的总余额，可以使用可计费模型上提供的 `balance` 方法。
该方法将返回一个以客户货币为单位的格式化字符串：

```php
$balance = $user->balance();
```

要为客户账户充值（增加余额），可以向 `creditBalance` 方法传入一个数值。
如果需要，还可以提供一个描述说明：

```php
$user->creditBalance(500, '高级客户充值。');
```

向 `debitBalance` 方法传入一个数值会从客户余额中扣除该金额：

```php
$user->debitBalance(300, '违规使用处罚。');
```

`applyBalance` 方法会为客户创建新的余额交易记录。
您可以使用 `balanceTransactions` 方法来获取这些交易记录，
这对于向客户展示充值和扣款日志非常有用：

```php
// 获取所有交易记录...
$transactions = $user->balanceTransactions();

foreach ($transactions as $transaction) {
    // 交易金额...
    $amount = $transaction->amount(); // $2.31

    // 获取相关的发票（如果有的话）...
    $invoice = $transaction->invoice();
}
```



### 税务 ID（Tax IDs）

Cashier 提供了一种简单的方式来管理客户的税务 ID。
例如，可以使用 `taxIds` 方法获取分配给某个客户的所有 [税务 ID](https://stripe.com/docs/api/customer_tax_ids/object) 集合：

```php
$taxIds = $user->taxIds();
```

您还可以通过税务 ID 的标识符来获取特定客户的某个税务 ID：

```php
$taxId = $user->findTaxId('txi_belgium');
```

您可以通过向 `createTaxId` 方法提供一个有效的 [类型](https://stripe.com/docs/api/customer_tax_ids/object#tax_id_object-type) 和值来创建一个新的税务 ID：

```php
$taxId = $user->createTaxId('eu_vat', 'BE0123456789');
```

`createTaxId` 方法会立即将增值税（VAT）ID 添加到客户账户中。
[Stripe 还会对增值税 ID 进行验证](https://stripe.com/docs/invoicing/customer/tax-ids#validation)，不过该验证过程是异步执行的。
您可以通过订阅 `customer.tax_id.updated` webhook 事件来获知验证状态的更新，并检查 [税务 ID 的 `verification` 参数](https://stripe.com/docs/api/customer_tax_ids/object#tax_id_object-verification)。
有关如何处理 webhook 的更多信息，请参阅[定义 webhook 处理程序的文档](#handling-stripe-webhooks)。

您可以使用 `deleteTaxId` 方法删除税务 ID：

```php
$user->deleteTaxId('txi_belgium');
```

### 同步客户数据与 Stripe

通常情况下，当您的应用用户更新了他们的姓名、电子邮件地址或其他同时存储在 Stripe 中的信息时，
您应当通知 Stripe 这些更新。
这样可以确保 Stripe 中保存的信息与您的应用数据保持同步。



为了实现自动同步，您可以在可计费（billable）模型上定义一个事件监听器，用于响应模型的 `updated` 事件。
然后，在事件监听器中调用模型的 `syncStripeCustomerDetails` 方法：

```php
use App\Models\User;
use function Illuminate\Events\queueable;

/**
 * 模型的 "booted" 方法。
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

现在，每当客户模型被更新时，其信息都会与 Stripe 同步。
为了方便起见，Cashier 会在客户首次创建时自动将客户信息与 Stripe 同步。

您可以通过重写 Cashier 提供的多个方法，来自定义同步客户信息到 Stripe 时所使用的字段。
例如，您可以重写 `stripeName` 方法，以自定义在 Cashier 同步客户信息到 Stripe 时，
应被视为客户“名称”的属性：

```php
/**
 * 获取应同步到 Stripe 的客户名称。
 */
public function stripeName(): string|null
{
    return $this->company_name;
}
```

类似地，您可以重写 `stripeEmail`、`stripePhone`、`stripeAddress` 和 `stripePreferredLocales` 方法。
在[更新 Stripe 客户对象](https://stripe.com/docs/api/customers/update)时，这些方法会将信息同步到相应的客户参数。
如果您希望完全控制客户信息的同步过程，可以重写 `syncStripeCustomerDetails` 方法。

### 结算门户（Billing Portal）

Stripe 提供了[一种简单的方式来设置结算门户](https://stripe.com/docs/billing/subscriptions/customer-portal)，
以便客户可以管理他们的订阅、支付方式，并查看账单历史。
您可以通过在控制器或路由中调用可计费模型的 `redirectToBillingPortal` 方法，
将用户重定向到结算门户：

```php
use Illuminate\Http\Request;

Route::get('/billing-portal', function (Request $request) {
    return $request->user()->redirectToBillingPortal();
});
```



默认情况下，当用户在管理完他们的订阅后，他们可以通过 Stripe 账单门户中的一个链接返回到你应用程序的 `home` 路由。
你可以通过将自定义 URL 作为参数传递给 `redirectToBillingPortal` 方法，来指定用户返回的自定义地址：

```php
use Illuminate\Http\Request;

Route::get('/billing-portal', function (Request $request) {
    return $request->user()->redirectToBillingPortal(route('billing'));
});
```

如果你希望生成账单门户的 URL，而不是生成一个 HTTP 重定向响应，可以调用 `billingPortalUrl` 方法：

```php
$url = $request->user()->billingPortalUrl(route('billing'));
```

## 支付方式

### 存储支付方式

为了使用 Stripe 创建订阅或执行“一次性”收费，你需要存储支付方式并从 Stripe 获取其标识符。
实现这一点的方法取决于你计划将该支付方式用于订阅还是单次收费。下面我们将分别进行说明。

#### 用于订阅的支付方式

当存储客户的信用卡信息以供未来订阅使用时，必须使用 Stripe 的 “Setup Intents” API 来安全地收集客户的支付方式信息。
“Setup Intent” 表示你打算向客户的支付方式收费。
Cashier 的 `Billable` trait 提供了 `createSetupIntent` 方法，可以方便地创建一个新的 Setup Intent。
你应当在用于渲染客户填写支付方式信息表单的路由或控制器中调用此方法：

```php
return view('update-payment-method', [
    'intent' => $user->createSetupIntent()
]);
```



在你创建了 Setup Intent 并将其传递给视图之后，你应该将其密钥（secret）附加到用于收集支付方式信息的元素上。
例如，考虑下面这个“更新支付方式”的表单：

```html
<input id="card-holder-name" type="text">

<!-- Stripe Elements 占位符 -->
<div id="card-element"></div>

<button id="card-button" data-secret="{{ $intent->client_secret }}">
    Update Payment Method
</button>
```

接下来，可以使用 Stripe.js 库将一个 [Stripe Element](https://stripe.com/docs/stripe-js) 附加到表单上，以安全地收集客户的支付信息：

```html
<script src="https://js.stripe.com/v3/"></script>

<script>
    const stripe = Stripe('stripe-public-key');

    const elements = stripe.elements();
    const cardElement = elements.create('card');

    cardElement.mount('#card-element');
</script>
```

接下来，可以使用 [Stripe 的 `confirmCardSetup` 方法](https://stripe.com/docs/js/setup_intents/confirm_card_setup) 来验证银行卡并从 Stripe 获取一个安全的“支付方式标识符”：

```js
const cardHolderName = document.getElementById('card-holder-name');
const cardButton = document.getElementById('card-button');
const clientSecret = cardButton.dataset.secret;

cardButton.addEventListener('click', async (e) => {
    const { setupIntent, error } = await stripe.confirmCardSetup(
        clientSecret, {
            payment_method: {
                card: cardElement,
                billing_details: { name: cardHolderName.value }
            }
        }
    );

    if (error) {
        // 向用户显示 “error.message” ...
    } else {
        // 卡片验证成功 ...
    }
});
```

在卡片被 Stripe 验证之后，你可以将生成的 `setupIntent.payment_method` 标识符传递给你的 Laravel 应用程序，并将其附加到该客户。
该支付方式可以被 [添加为新的支付方式](#adding-payment-methods)，或者 [用于更新默认支付方式](#updating-the-default-payment-method)。
你也可以立即使用该支付方式标识符来 [创建一个新的订阅](#creating-subscriptions)。

> [!注意]
> 如果你想了解更多关于 Setup Intents 和收集客户支付信息的内容，请参阅 [Stripe 提供的这篇概述](https://stripe.com/docs/payments/save-and-reuse#php)。



#### 用于单次收费的支付方式（Payment Methods for Single Charges）

当然，当对客户的支付方式进行单次收费时，我们只需要使用一次支付方式标识符。
由于 Stripe 的限制，你不能使用客户已存储的默认支付方式来执行单次收费。
你必须允许客户通过 Stripe.js 库输入他们的支付信息。
例如，考虑以下表单：

```html
<input id="card-holder-name" type="text">

<!-- Stripe Elements 占位符 -->
<div id="card-element"></div>

<button id="card-button">
    Process Payment
</button>
```

在定义了这样的表单后，可以使用 Stripe.js 库将一个 [Stripe Element](https://stripe.com/docs/stripe-js) 附加到表单上，以安全地收集客户的支付信息：

```html
<script src="https://js.stripe.com/v3/"></script>

<script>
    const stripe = Stripe('stripe-public-key');

    const elements = stripe.elements();
    const cardElement = elements.create('card');

    cardElement.mount('#card-element');
</script>
```

接下来，可以使用 [Stripe 的 `createPaymentMethod` 方法](https://stripe.com/docs/stripe-js/reference#stripe-create-payment-method) 来验证银行卡，并从 Stripe 获取一个安全的“支付方式标识符”：

```js
const cardHolderName = document.getElementById('card-holder-name');
const cardButton = document.getElementById('card-button');

cardButton.addEventListener('click', async (e) => {
    const { paymentMethod, error } = await stripe.createPaymentMethod(
        'card', cardElement, {
            billing_details: { name: cardHolderName.value }
        }
    );

    if (error) {
        // 向用户显示 “error.message” ...
    } else {
        // 卡片验证成功 ...
    }
});
```

如果银行卡验证成功，你可以将 `paymentMethod.id` 传递给你的 Laravel 应用程序，以便处理一次性[单次收费](#simple-charge)。



### 获取支付方式（Retrieving Payment Methods）

在可计费（billable）模型实例上调用 `paymentMethods` 方法，会返回一个包含多个 `Laravel\Cashier\PaymentMethod` 实例的集合：

```php
$paymentMethods = $user->paymentMethods();
```

默认情况下，此方法会返回所有类型的支付方式。
如果你想获取特定类型的支付方式，可以将 `type` 作为参数传递给该方法：

```php
$paymentMethods = $user->paymentMethods('sepa_debit');
```

要获取客户的默认支付方式，可以使用 `defaultPaymentMethod` 方法：

```php
$paymentMethod = $user->defaultPaymentMethod();
```

你还可以使用 `findPaymentMethod` 方法来获取附加到该可计费模型的特定支付方式：

```php
$paymentMethod = $user->findPaymentMethod($paymentMethodId);
```

### 支付方式存在性（Payment Method Presence）

要判断一个可计费模型的账户中是否附加了默认支付方式，可以调用 `hasDefaultPaymentMethod` 方法：

```php
if ($user->hasDefaultPaymentMethod()) {
    // ...
}
```

你可以使用 `hasPaymentMethod` 方法来判断该模型是否至少附加了一个支付方式：

```php
if ($user->hasPaymentMethod()) {
    // ...
}
```

此方法会判断模型是否拥有任何支付方式。
若要判断模型是否拥有特定类型的支付方式，可以将 `type` 作为参数传递给该方法：

```php
if ($user->hasPaymentMethod('sepa_debit')) {
    // ...
}
```

### 更新默认支付方式（Updating the Default Payment Method）

可以使用 `updateDefaultPaymentMethod` 方法来更新客户的默认支付方式信息。
该方法接受一个 Stripe 支付方式标识符，并将其设置为新的默认账单支付方式：

```php
$user->updateDefaultPaymentMethod($paymentMethod);
```

要将本地的默认支付方式信息与 Stripe 上客户的默认支付方式信息同步，可以使用 `updateDefaultPaymentMethodFromStripe` 方法：

```php
$user->updateDefaultPaymentMethodFromStripe();
```

> [!警告]
> 客户的默认支付方式只能用于开发票（invoicing）和创建新的订阅。
由于 Stripe 的限制，它不能用于单次收费（single charges）。



### 添加支付方式（Adding Payment Methods）

要添加新的支付方式，可以在可计费（billable）模型上调用 `addPaymentMethod` 方法，并传入支付方式标识符：

```php
$user->addPaymentMethod($paymentMethod);
```

> [!注意]
> 要了解如何获取支付方式标识符，请查看[支付方式存储文档](#storing-payment-methods)。

### 删除支付方式（Deleting Payment Methods）

要删除某个支付方式，可以在你想删除的 `Laravel\Cashier\PaymentMethod` 实例上调用 `delete` 方法：

```php
$paymentMethod->delete();
```

`deletePaymentMethod` 方法可以从可计费模型中删除特定的支付方式：

```php
$user->deletePaymentMethod('pm_visa');
```

`deletePaymentMethods` 方法会删除可计费模型的所有支付方式信息：

```php
$user->deletePaymentMethods();
```

默认情况下，此方法会删除所有类型的支付方式。
若要删除特定类型的支付方式，可以将 `type` 作为参数传递给该方法：

```php
$user->deletePaymentMethods('sepa_debit');
```

> [!警告]
> 如果用户拥有一个活跃的订阅，你的应用程序不应允许他们删除其默认支付方式。

## 订阅（Subscriptions）

订阅提供了一种为客户设置定期付款的方式。
由 Cashier 管理的 Stripe 订阅支持多订阅价格、订阅数量、试用期等功能。

### 创建订阅（Creating Subscriptions）

要创建订阅，首先需要获取你的可计费模型实例（通常是 `App\Models\User` 的实例）。
在获取到模型实例后，你可以使用 `newSubscription` 方法来创建该模型的订阅：

```php
use Illuminate\Http\Request;

Route::post('/user/subscribe', function (Request $request) {
    $request->user()->newSubscription(
        'default', 'price_monthly'
    )->create($request->paymentMethodId);

    // ...
});
```



传递给 `newSubscription` 方法的第一个参数应该是订阅的内部类型。
如果你的应用程序只提供单一订阅，你可以将其命名为 `default` 或 `primary`。
这种订阅类型仅供应用程序内部使用，不用于展示给用户。
此外，它不应包含空格，并且在创建订阅之后绝不应该被更改。

第二个参数是用户正在订阅的具体价格。该值应当与 Stripe 中价格的标识符相对应。

`create` 方法，它接受 [一个 Stripe 支付方式标识符](#storing-payment-methods) 或 Stripe `PaymentMethod` 对象，将会启动订阅，并更新你的数据库，包括可计费模型的 Stripe 客户 ID 以及其他相关的计费信息。

> [!警告]
> 直接将支付方式标识符传递给 `create` 订阅方法也会自动将其添加到用户已保存的支付方式中。

#### 通过发票邮件收取循环付款

你可以不自动收取客户的循环付款，而是指示 Stripe 在每次循环付款到期时向客户发送一封发票邮件。然后客户可以在收到发票后手动支付。在通过发票收取循环付款时，客户不需要提前提供支付方式：

```php
$user->newSubscription('default', 'price_monthly')->createAndSendInvoice();
```

客户必须在订阅被取消之前支付他们的发票，这个期限由 `days_until_due` 选项决定。
默认情况下是 30 天；不过，如果你愿意，你可以为此选项提供一个特定的值：

```php
$user->newSubscription('default', 'price_monthly')->createAndSendInvoice([], [
    'days_until_due' => 30
]);
```



#### 数量(Quantities)

如果你想在创建订阅时为该价格设置一个特定的[数量](https://stripe.com/docs/billing/subscriptions/quantities)，你应该在创建订阅之前，在订阅构造器上调用 `quantity` 方法：

```php
$user->newSubscription('default', 'price_monthly')
    ->quantity(5)
    ->create($paymentMethod);
```

#### 其他详细信息(Additional Details)

如果你想指定 Stripe 所支持的额外[客户](https://stripe.com/docs/api/customers/create)或[订阅](https://stripe.com/docs/api/subscriptions/create)选项，你可以将它们作为第二和第三个参数传递给 `create` 方法：

```php
$user->newSubscription('default', 'price_monthly')->create($paymentMethod, [
    'email' => $email,
], [
    'metadata' => ['note' => 'Some extra information.'],
]);
```

#### 优惠券(Coupons)

如果你想在创建订阅时应用一个优惠券，你可以使用 `withCoupon` 方法：

```php
$user->newSubscription('default', 'price_monthly')
    ->withCoupon('code')
    ->create($paymentMethod);
```

或者，如果你想应用一个[Stripe 促销代码](https://stripe.com/docs/billing/subscriptions/discounts/codes)，你可以使用 `withPromotionCode` 方法：

```php
$user->newSubscription('default', 'price_monthly')
    ->withPromotionCode('promo_code_id')
    ->create($paymentMethod);
```

给定的促销代码 ID 应当是 Stripe 分配给该促销代码的 API ID，而不是面向客户的促销代码。
如果你需要根据一个面向客户的促销代码查找促销代码 ID，你可以使用 `findPromotionCode` 方法：

```php
// 根据面向客户的代码查找促销代码 ID...
$promotionCode = $user->findPromotionCode('SUMMERSALE');

// 根据面向客户的代码查找一个“有效的”活动促销代码 ID...
$promotionCode = $user->findActivePromotionCode('SUMMERSALE');
```



在上面的示例中，返回的 `$promotionCode` 对象是 `Laravel\Cashier\PromotionCode` 的一个实例。
这个类包装了一个底层的 `Stripe\PromotionCode` 对象。
你可以通过调用 `coupon` 方法来获取与该促销代码相关联的优惠券：

```php
$coupon = $user->findPromotionCode('SUMMERSALE')->coupon();
```

该优惠券实例允许你判断折扣金额，以及该优惠券表示的是固定金额折扣还是百分比折扣

```php
if ($coupon->isPercentage()) {
    return $coupon->percentOff().'%'; // 21.5%
} else {
    return $coupon->amountOff(); // $5.99
}
```

你还可以检索当前应用于某个客户或订阅的折扣：

```php
$discount = $billable->discount();

$discount = $subscription->discount();
```

返回的 `Laravel\Cashier\Discount` 实例包装了一个底层的 `Stripe\Discount` 对象实例。
你可以通过调用 `coupon` 方法来检索与该折扣相关的优惠券：

```php
$coupon = $subscription->discount()->coupon();
```

如果你想将一个新的优惠券或促销代码应用到某个客户或订阅上，你可以通过 `applyCoupon` 或 `applyPromotionCode` 方法来实现：

```php
$billable->applyCoupon('coupon_id');
$billable->applyPromotionCode('promotion_code_id');

$subscription->applyCoupon('coupon_id');
$subscription->applyPromotionCode('promotion_code_id');
```

请记住，你应该使用 Stripe 分配给促销代码的 API ID，而不是面向客户的促销代码。
在任意时刻，只有一个优惠券或促销代码可以被应用到某个客户或订阅上。

如需关于该主题的更多信息，请参考 Stripe 文档中有关[优惠券](https://stripe.com/docs/billing/subscriptions/coupons)和[促销代码](https://stripe.com/docs/billing/subscriptions/coupons/codes)的内容。



#### 添加订阅

如果你想为一个已经拥有默认支付方式的客户添加订阅，你可以在订阅构造器上调用 `add` 方法：

```php
use App\Models\User;

$user = User::find(1);

$user->newSubscription('default', 'price_monthly')->add();
```

#### 从 Stripe 仪表盘创建订阅 (Creating Subscriptions From the Stripe Dashboard)

你也可以直接在 Stripe 仪表盘中创建订阅。
在这样做时，Cashier 会同步新添加的订阅，并将它们分配为 `default` 类型。
若要自定义分配给通过仪表盘创建的订阅的订阅类型，你可以[定义 webhook 事件处理程序](#defining-webhook-event-handlers)。

此外，你只能通过 Stripe 仪表盘创建一种类型的订阅。
如果你的应用提供多种使用不同类型的订阅，那么通过 Stripe 仪表盘只能添加其中一种订阅类型。

最后，你应该始终确保每种订阅类型在你的应用中只为客户添加一个活跃订阅。
如果一个客户拥有两个 `default` 订阅，即使两者都会与应用的数据库同步，Cashier 也只会使用最近添加的那个订阅。

#### 检查订阅状态 (Checking Subscription Status)

一旦客户订阅了你的应用，你可以使用多种便捷方法轻松检查其订阅状态。
首先，如果客户拥有一个活跃订阅，即使该订阅当前处于试用期，`subscribed` 方法也会返回 `true`。
`subscribed` 方法将订阅的类型作为第一个参数：

```php
if ($user->subscribed('default')) {
    // ...
}
```



`subscribed` 方法也是一个很好的[路由中间件](/docs/laravel/12.x/middleware)候选，可以根据用户的订阅状态来过滤对路由和控制器的访问：

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureUserIsSubscribed
{
    /**
     * 处理一个传入请求。
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        if ($request->user() && ! $request->user()->subscribed('default')) {
            // 该用户不是付费客户...
            return redirect('/billing');
        }

        return $next($request);
    }
}
```

如果你想判断用户是否仍处于试用期，你可以使用 `onTrial` 方法。
该方法可用于判断是否应向用户显示他们仍在试用期的提示：

```php
if ($user->subscription('default')->onTrial()) {
    // ...
}
```

`subscribedToProduct` 方法可用于判断用户是否订阅了指定产品，该产品基于给定的 Stripe 产品标识符。
在 Stripe 中，产品是一组价格的集合。
在此示例中，我们将判断用户的 `default` 订阅是否已主动订阅应用程序的 “premium” 产品。
给定的 Stripe 产品标识符应对应于 Stripe 仪表盘中你产品的某一个标识符：

```php
if ($user->subscribedToProduct('prod_premium', 'default')) {
    // ...
}
```

通过向 `subscribedToProduct` 方法传递一个数组，你可以判断用户的 `default` 订阅是否已主动订阅应用程序的 “basic” 或 “premium” 产品：

```php
if ($user->subscribedToProduct(['prod_basic', 'prod_premium'], 'default')) {
    // ...
}
```



`subscribedToPrice` 方法可用于判断某个客户的订阅是否对应给定的价格 ID：

```php
if ($user->subscribedToPrice('price_basic_monthly', 'default')) {
    // ...
}
```

`recurring` 方法可用于判断用户当前是否已订阅并且不再处于试用期内：

```php
if ($user->subscription('default')->recurring()) {
    // ...
}
```

> [!警告]
> 如果一个用户拥有两个相同类型的订阅，`subscription` 方法将始终返回最新的订阅。例如，一个用户可能拥有两个类型为 `default` 的订阅记录；然而，其中一个订阅可能是旧的、已过期的订阅，而另一个是当前的、有效的订阅。此时会始终返回最新的订阅，而较旧的订阅会保留在数据库中用于历史查看。

### 取消订阅状态

要确定用户是否曾经是活跃订阅者但已取消订阅，你可以使用 `canceled` 方法：

```php
if ($user->subscription('default')->canceled()) {
    // ...
}
```

你也可以判断用户是否已经取消订阅但仍处于他们的“宽限期”（grace period）直到订阅完全过期。例如，如果用户在 3 月 5 日取消了订阅，而该订阅原本计划在 3 月 10 日过期，那么用户将在 3 月 10 日之前处于“宽限期”。请注意，在这段时间内，`subscribed` 方法仍然返回 `true`：

```php
if ($user->subscription('default')->onGracePeriod()) {
    // ...
}
```

要判断用户是否已经取消订阅并且不再处于“宽限期”内，你可以使用 `ended` 方法：

```php
if ($user->subscription('default')->ended()) {
    // ...
}
```



#### 未完成支付与逾期状态说明

如果一个订阅在创建之后需要执行二次支付操作，那么该订阅将被标记为 `incomplete`。订阅状态储存在 Cashier 的 `subscriptions` 数据表中的 `stripe_status` 列里。

类似地，如果在切换价格（swapping prices）时需要执行二次支付操作，那么该订阅将被标记为 `past_due`。当你的订阅处于这两种状态中的任一种时，在客户确认他们的付款之前，它都不会处于激活状态。要判断某个订阅是否有未完成的付款，可以在计费模型（billable model）或订阅实例上使用 `hasIncompletePayment` 方法：

```php
if ($user->hasIncompletePayment('default')) {
    // ...
}

if ($user->subscription('default')->hasIncompletePayment()) {
    // ...
}
```

当一个订阅有未完成的付款时，你应该将用户引导到 Cashier 的付款确认页面，并传递 `latestPayment` 标识符。你可以使用订阅实例上可用的 `latestPayment` 方法来获取这个标识符：

```html
<a href="{{ route('cashier.payment', $subscription->latestPayment()->id) }}">
    Please confirm your payment.
</a>
```

如果你希望在订阅处于 `past_due` 或 `incomplete` 状态时仍将其视为已激活（active），你可以使用 Cashier 提供的 `keepPastDueSubscriptionsActive` 与 `keepIncompleteSubscriptionsActive` 方法。通常，这些方法应在 `App\Providers\AppServiceProvider` 的 `register` 方法中被调用：

```php
use Laravel\Cashier\Cashier;

/**
 * 注册应用程序所需的所有服务。
 */
public function register(): void
{
    Cashier::keepPastDueSubscriptionsActive();
    Cashier::keepIncompleteSubscriptionsActive();
}
```

> [!警告]
> 当订阅处于 `incomplete` 状态时，在付款确认之前，它无法被更改。因此，当订阅处于 `incomplete` 状态时，`swap` 和 `updateQuantity` 方法将抛出异常。



#### 订阅作用域

大多数订阅状态也可作为查询作用域使用，这样你就可以轻松查询数据库中处于某一特定状态的订阅：

```php
// 获取所有激活的订阅...
$subscriptions = Subscription::query()->active()->get();

// 获取某个用户所有已取消的订阅...
$subscriptions = $user->subscriptions()->canceled()->get();
```

A complete list of available scopes is available below:

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

### 更改价格

在客户订阅你的应用程序之后，他们可能偶尔会希望更改为新的订阅价格。要将客户切换到新的价格，将 Stripe 价格的标识符传递给 `swap` 方法。在切换价格时，假定用户希望在之前已取消的情况下重新激活他们的订阅。所给的价格标识符应对应 Stripe 控制台中可用的 Stripe 价格标识符：

```php
use App\Models\User;

$user = App\Models\User::find(1);

$user->subscription('default')->swap('price_yearly');
```

如果客户处于试用期内，试用期将被保留。此外，如果订阅存在“数量”，该数量也会被保留。

如果你希望在切换价格的同时取消客户当前的任何试用期，你可以调用 `skipTrial` 方法：

```php
$user->subscription('default')
    ->skipTrial()
    ->swap('price_yearly');
```



如果你希望在切换价格时立即向客户开具账单，而不是等待他们的下一个计费周期，你可以使用 `swapAndInvoice` 方法：

```php
$user = User::find(1);

$user->subscription('default')->swapAndInvoice('price_yearly');
```

#### 按比例分摊

默认情况下，在切换不同价格时，Stripe 会对费用进行按比例分摊。`noProrate` 方法可用于在不进行按比例分摊的情况下更新订阅的价格：

```php
$user->subscription('default')->noProrate()->swap('price_yearly');
```

关于订阅按比例分摊的更多信息，请参阅 [Stripe 文档](https://stripe.com/docs/billing/subscriptions/prorations)。

> [!警告]
> 在 `swapAndInvoice` 方法之前执行 `noProrate` 方法对按比例分摊不会产生任何影响。发票将始终被开具。

### 订阅数量

有时，订阅会受“数量”的影响。例如，一个项目管理应用可能会按每个项目每月 10 美元收费。你可以使用 `incrementQuantity` 和 `decrementQuantity` 方法来轻松增加或减少订阅数量：

```php
use App\Models\User;

$user = User::find(1);

$user->subscription('default')->incrementQuantity();

// 在订阅当前数量上增加五个...
$user->subscription('default')->incrementQuantity(5);

$user->subscription('default')->decrementQuantity();

// 在订阅当前数量上减少五个...
$user->subscription('default')->decrementQuantity(5);
```

或者，你可以使用 `updateQuantity` 方法设置一个特定数量：

```php
$user->subscription('default')->updateQuantity(10);
```

`noProrate` 方法可以用于在不进行按比例分摊的情况下更新订阅数量：

```php
$user->subscription('default')->noProrate()->updateQuantity(10);
```

关于订阅数量的更多信息，请参阅 [Stripe 文档](https://stripe.com/docs/subscriptions/quantities)。



#### 包含多个产品的订阅的数量

如果你的订阅是[带有多个产品的订阅](#subscriptions-with-multiple-products)，那么你应当将你希望递增或递减数量的价格 ID 作为第二个参数传递给 increment / decrement 方法：

```php
$user->subscription('default')->incrementQuantity(1, 'price_chat');
```

### 包含多个产品的订阅

[带有多个产品的订阅](https://stripe.com/docs/billing/subscriptions/multiple-products)允许你将多个计费产品分配给一个单一的订阅。例如，假设你正在构建一个客户服务“帮助台”应用程序，它的基础订阅价格是每月 10 美元，但提供一个额外的实时聊天附加产品，每月额外收费 15 美元。有关带有多个产品的订阅的信息存储在 Cashier 的 `subscription_items` 数据表中。

你可以通过将一个价格数组作为第二个参数传递给 `newSubscription` 方法，为某个订阅指定多个产品：

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

在上述示例中，客户将有两个价格附加到他们的 `default` 订阅上。这两个价格都会根据它们各自的计费周期进行收费。如有必要，你可以使用 `quantity` 方法为每个价格指定特定数量：

```php
$user = User::find(1);

$user->newSubscription('default', ['price_monthly', 'price_chat'])
    ->quantity(5, 'price_chat')
    ->create($paymentMethod);
```

如果你希望向一个已有订阅添加另一个价格，你可以调用订阅的 `addPrice` 方法：

```php
$user = User::find(1);

$user->subscription('default')->addPrice('price_chat');
```



上述示例会添加新的价格，并且客户会在他们的下一个计费周期被收取费用。
如果你想立即向客户收费，你可以使用 `addPriceAndInvoice` 方法：

```php
$user->subscription('default')->addPriceAndInvoice('price_chat');
```

如果你想以特定数量添加一个价格，你可以将数量作为第二个参数传递给 `addPrice` 或 `addPriceAndInvoice` 方法：

```php
$user = User::find(1);

$user->subscription('default')->addPrice('price_chat', 5);
```

你可以使用 `removePrice` 方法从订阅中移除价格：

```php
$user->subscription('default')->removePrice('price_chat');
```

> [!警告]
> 你不能移除订阅中的最后一个价格。相反，你应该直接取消订阅。

#### 交换价格（Swapping Prices）

你也可以更改附加在包含多个产品的订阅上的价格。
例如，想象一个客户有一个带有 `price_chat` 附加产品的 `price_basic` 订阅，而你想将该客户从 `price_basic` 升级到 `price_pro`：

```php
use App\Models\User;

$user = User::find(1);

$user->subscription('default')->swap(['price_pro', 'price_chat']);
```

执行上述示例时，带有 `price_basic` 的底层订阅项会被删除，而带有 `price_chat` 的订阅项会被保留。并且，会创建一个新的 `price_pro` 订阅项。

你也可以通过向 `swap` 方法传递一个键/值对数组来指定订阅项选项。例如，你可能需要指定订阅价格的数量：

```php
$user = User::find(1);

$user->subscription('default')->swap([
    'price_pro' => ['quantity' => 5],
    'price_chat'
]);
```



如果你想在订阅上交换单个价格，你可以在订阅项本身上使用 `swap` 方法来完成。
这种方法在你希望保留订阅中其他价格的所有现有元数据时特别有用：

```php
$user = User::find(1);

$user->subscription('default')
    ->findItemOrFail('price_basic')
    ->swap('price_pro');
```

#### 按比例分摊（Proration）

默认情况下，当在包含多个产品的订阅中添加或移除价格时，Stripe 会按比例分摊费用。
如果你想在不进行按比例分摊的情况下进行价格调整，你应该将 `noProrate` 方法链式调用到你的价格操作上：

```php
$user->subscription('default')->noProrate()->removePrice('price_chat');
```

#### 数量（Quantities）

如果你想更新单个订阅价格的数量，你可以使用**现有的数量方法**（existing quantity methods），并将价格的 ID 作为额外参数传递给该方法：

```php
$user = User::find(1);

$user->subscription('default')->incrementQuantity(5, 'price_chat');

$user->subscription('default')->decrementQuantity(3, 'price_chat');

$user->subscription('default')->updateQuantity(10, 'price_chat');
```

> [!警告]
> 当一个订阅有多个价格时，`Subscription` 模型上的 `stripe_price` 和 `quantity` 属性将为 `null`。要访问单个价格的属性，你应该使用 `Subscription` 模型提供的 `items` 关系。

#### 订阅项（Subscription Items）

当一个订阅有多个价格时，它会在数据库的 `subscription_items` 表中拥有多个订阅 “items”。你可以通过订阅上的 `items` 关系来访问这些项：

```php
use App\Models\User;

$user = User::find(1);

$subscriptionItem = $user->subscription('default')->items->first();

// 获取特定项的 Stripe 价格和数量...
$stripePrice = $subscriptionItem->stripe_price;
$quantity = $subscriptionItem->quantity;
```



你也可以使用 `findItemOrFail` 方法检索特定的价格：

```php
$user = User::find(1);

$subscriptionItem = $user->subscription('default')->findItemOrFail('price_chat');
```

### 多个订阅（Multiple Subscriptions）

Stripe 允许你的客户同时拥有多个订阅。
例如，你可能经营一家健身房，提供游泳订阅和举重订阅，并且每个订阅可能有不同的定价。
当然，客户应该能够订阅其中一个或两个计划。

当你的应用程序创建订阅时，你可以将订阅的类型提供给 `newSubscription` 方法。
该类型可以是任何字符串，用来表示用户正在启动的订阅类型：

```php
use Illuminate\Http\Request;

Route::post('/swimming/subscribe', function (Request $request) {
    $request->user()->newSubscription('swimming')
        ->price('price_swimming_monthly')
        ->create($request->paymentMethodId);

    // ...
});
```

在这个示例中，我们为客户启动了一个按月计费的游泳订阅。
然而，他们可能会在稍后时间希望切换到按年计费的订阅。
在调整客户的订阅时，我们只需交换 `swimming` 订阅上的价格即可：

```php
$user->subscription('swimming')->swap('price_swimming_yearly');
```

当然，你也可以完全取消该订阅：

```php
$user->subscription('swimming')->cancel();
```

### 基于用量计费（Usage Based Billing）

[基于用量计费](https://stripe.com/docs/billing/subscriptions/metered-billing) 允许你根据客户在计费周期内的产品使用量向他们收费。
例如，你可能会根据客户每月发送的短信数或电子邮件数量进行收费。

要开始使用用量计费，你首先需要在 Stripe 控制台中创建一个带有
[基于用量的计费模型](https://docs.stripe.com/billing/subscriptions/usage-based/implementation-guide) 和一个
[meter（计量器）](https://docs.stripe.com/billing/subscriptions/usage-based/recording-usage#configure-meter) 的新产品。
在创建计量器之后，存储相关的事件名称和计量器 ID，因为你需要它们来报告和检索用量。
然后，使用 `meteredPrice` 方法将按用量计费的价格 ID 添加到客户订阅中：

```php
use Illuminate\Http\Request;

Route::post('/user/subscribe', function (Request $request) {
    $request->user()->newSubscription('default')
        ->meteredPrice('price_metered')
        ->create($request->paymentMethodId);

    // ...
});
```



你也可以通过 [Stripe Checkout](#checkout) 启动一个按用量计费的订阅：

```php
$checkout = Auth::user()
    ->newSubscription('default', [])
    ->meteredPrice('price_metered')
    ->checkout();

return view('your-checkout-view', [
    'checkout' => $checkout,
]);
```

#### 报告用量（Reporting Usage）

当你的客户使用你的应用程序时，你将向 Stripe 报告他们的使用量，以便他们能够被准确计费。
要报告一个按用量计费事件的使用量，你可以在你的 `Billable` 模型上使用 `reportMeterEvent` 方法：

```php
$user = User::find(1);

$user->reportMeterEvent('emails-sent');
```

默认情况下，会将一个“使用数量”（usage quantity）1 添加到计费周期中。
或者，你可以传递一个特定数量的 “usage”，将其添加到该计费周期内用户的使用量中：

```php
$user = User::find(1);

$user->reportMeterEvent('emails-sent', quantity: 15);
```

要检索客户某个 meter 的事件摘要，你可以使用 `Billable` 实例的 `meterEventSummaries` 方法：

```php
$user = User::find(1);

$meterUsage = $user->meterEventSummaries($meterId);

$meterUsage->first()->aggregated_value // 10
```

关于 meter 事件摘要的更多信息，请参考 Stripe 的
[Meter Event Summary 对象文档](https://docs.stripe.com/api/billing/meter-event_summary/object)。

要[列出所有 meters](https://docs.stripe.com/api/billing/meter/list)，你可以使用 `Billable` 实例的 `meters` 方法：

```php
$user = User::find(1);

$user->meters();
```

### 订阅税（Subscription Taxes）

> [!警告]
> 与其手动计算税率，你可以使用 [Stripe Tax 自动计算税费](#tax-configuration)

要指定用户在订阅上支付的税率，你应该在你的 billable 模型上实现 `taxRates` 方法，并返回一个包含 Stripe 税率 ID 的数组。
你可以在[你的 Stripe 控制台](https://dashboard.stripe.com/test/tax-rates)中定义这些税率：

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



`taxRates` 方法使你能够基于每个客户来应用税率，这对于拥有跨多个国家和税率的用户群体可能会很有帮助。

如果你提供包含多个产品的订阅，你可以通过在 billable 模型上实现 `priceTaxRates` 方法，为每个价格定义不同的税率：

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

> [!警告]
> `taxRates` 方法仅适用于订阅收费。如果你使用 Cashier 进行“一次性”收费，你需要在当时手动指定税率。

#### 同步税率（Syncing Tax Rates）

当更改 `taxRates` 方法返回的硬编码税率 ID 时，该用户的任何现有订阅上的税务设置将保持不变。
如果你希望使用新的 `taxRates` 值更新现有订阅的税值，你应该在用户的订阅实例上调用 `syncTaxRates` 方法：

```php
$user->subscription('default')->syncTaxRates();
```

这也会同步具有多个产品的订阅的任何项目税率。
如果你的应用程序提供包含多个产品的订阅，你应该确保你的 billable 模型实现了前文讨论的 `priceTaxRates` 方法（见上方的 **订阅税** 部分）。

#### 税务豁免（Tax Exemption）

Cashier 还提供了 `isNotTaxExempt`、`isTaxExempt` 和 `reverseChargeApplies` 方法，用于确定客户是否免税。
这些方法将调用 Stripe API 以确定客户的税务豁免状态：

```php
use App\Models\User;

$user = User::find(1);

$user->isTaxExempt();
$user->isNotTaxExempt();
$user->reverseChargeApplies();
```

> [!警告]
> 这些方法在任何 `Laravel\Cashier\Invoice` 对象上也可用。
然而，当在 `Invoice` 对象上调用时，这些方法将根据发票创建时的状态来确定豁免情况。



### 订阅锚定日期（Subscription Anchor Date）

默认情况下，计费周期锚点是订阅创建的日期；如果使用了试用期，则为试用期结束的日期。如果你希望修改计费锚定日期，可以使用 `anchorBillingCycleOn` 方法：

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

### 取消订阅（Cancelling Subscriptions）

要取消订阅，请在用户的订阅上调用 `cancel` 方法：

```php
$user->subscription('default')->cancel();
```

当订阅被取消时，Cashier 会自动设置你 `subscriptions` 数据库表中的 `ends_at` 列。该列用于判断 `subscribed` 方法何时应开始返回 `false`。

例如，如果客户在 3 月 1 日取消了订阅，但该订阅原本计划在 3 月 5 日才结束，那么在 3 月 5 日之前，`subscribed` 方法仍会返回 `true`。这样做是因为通常允许用户在其计费周期结束之前继续使用应用程序。

你可以使用 `onGracePeriod` 方法来判断用户是否已经取消订阅但仍处于“宽限期”内：

```php
if ($user->subscription('default')->onGracePeriod()) {
    // ...
}
```

如果你希望立即取消订阅，请在用户的订阅上调用 `cancelNow` 方法：

```php
$user->subscription('default')->cancelNow();
```



如果你希望**立即取消订阅**，并**为任何尚未开具发票的计量使用量或新的 / 待处理的按比例计费发票项目开具发票**，可以在用户的订阅上调用 `cancelNowAndInvoice` 方法：

```php
$user->subscription('default')->cancelNowAndInvoice();
```

你也可以选择在**某个特定时间点**取消订阅：

```php
$user->subscription('default')->cancelAt(
    now()->addDays(10)
);
```

最后，在删除关联的用户模型之前，你应当始终先取消用户的订阅：

```php
$user->subscription('default')->cancelNow();

$user->delete();
```

### 恢复订阅（Resuming Subscriptions）

如果客户已经取消了订阅，而你希望恢复该订阅，你可以在订阅上调用 `resume` 方法。客户必须仍然处于其“宽限期”内，才能恢复订阅：

```php
$user->subscription('default')->resume();
```

如果客户取消订阅后，在订阅完全过期之前恢复了该订阅，则客户不会被立即扣费。相反，订阅将被重新激活，并且客户将按照**原始的计费周期**进行计费。


## 订阅试用（Subscription Trials）

### 预先提供付款方式（With Payment Method Up Front）

如果你希望在**仍然提前收集付款方式信息**的情况下向客户提供试用期，那么在创建订阅时应使用 `trialDays` 方法：

```php
use Illuminate\Http\Request;

Route::post('/user/subscribe', function (Request $request) {
    $request->user()->newSubscription('default', 'price_monthly')
        ->trialDays(10)
        ->create($request->paymentMethodId);

    // ...
});
```

该方法会在数据库中的订阅记录上设置试用期结束日期，并指示 Stripe 在此日期之后才开始向客户计费。使用 `trialDays` 方法时，Cashier 会覆盖在 Stripe 中为该价格配置的任何默认试用期。

> [!警告]
> 如果在试用期结束日期之前未取消客户的订阅，那么试用期一结束就会立即向客户收费，因此你应当确保通知用户其试用期的结束日期。



`trialUntil` 方法允许你提供一个 `DateTime` 实例，用于指定试用期应在何时结束：

```php
use Carbon\Carbon;

$user->newSubscription('default', 'price_monthly')
    ->trialUntil(Carbon::now()->addDays(10))
    ->create($paymentMethod);
```

你可以使用**用户实例的** `onTrial` 方法，或**订阅实例的** `onTrial` 方法来判断用户是否处于试用期内。下面两个示例是等价的：

```php
if ($user->onTrial('default')) {
    // ...
}

if ($user->subscription('default')->onTrial()) {
    // ...
}
```

你可以使用 `endTrial` 方法来**立即结束**订阅试用期：

```php
$user->subscription('default')->endTrial();
```

要判断一个**现有的试用期是否已经过期**，可以使用 `hasExpiredTrial` 方法：

```php
if ($user->hasExpiredTrial('default')) {
    // ...
}

if ($user->subscription('default')->hasExpiredTrial()) {
    // ...
}
```

#### 在 Stripe / Cashier 中定义试用天数（Defining Trial Days in Stripe / Cashier）

你可以选择在 Stripe 仪表盘中定义你的价格所包含的试用天数，或者始终通过 Cashier 显式传递试用天数。如果你选择在 Stripe 中定义价格的试用天数，需要注意的是：**新的订阅（包括曾经订阅过的客户再次创建的新订阅）都会自动获得试用期**，除非你显式调用 `skipTrial()` 方法。

### 不预先提供付款方式（Without Payment Method Up Front）

如果你希望在**不提前收集用户付款方式信息**的情况下提供试用期，你可以在用户记录上将 `trial_ends_at` 列设置为你期望的试用结束日期。这通常在用户注册期间完成：

```php
use App\Models\User;

$user = User::create([
    // ...
    'trial_ends_at' => now()->addDays(10),
]);
```

> [!警告]
> 请务必在你的可计费模型（billable model）类定义中，为 `trial_ends_at` 属性添加一个 [日期类型转换（date cast）](/docs/laravel/12.x/eloquent-mutators#date-casting)。



Cashier 将这种类型的试用称为“**通用试用（generic trial）**”，因为它并未关联到任何现有的订阅。如果当前日期尚未超过 `trial_ends_at` 的值，那么在可计费模型实例上调用 `onTrial` 方法将返回 `true`：

```php
if ($user->onTrial()) {
    // 用户正处于试用期内……
}
```

当你准备为用户创建一个**实际的订阅**时，可以像往常一样使用 `newSubscription` 方法：

```php
$user = User::find(1);

$user->newSubscription('default', 'price_monthly')->create($paymentMethod);
```

要获取用户的试用结束日期，可以使用 `trialEndsAt` 方法。如果用户正处于试用期，该方法将返回一个 Carbon 日期实例；如果用户未处于试用期，则返回 `null`。如果你希望获取**非默认订阅类型**的试用结束日期，还可以传递一个可选的订阅类型参数：

```php
if ($user->onTrial()) {
    $trialEndsAt = $user->trialEndsAt('main');
}
```

如果你希望明确判断用户是否正处于其“**通用试用**”期内，并且尚未创建任何实际订阅，也可以使用 `onGenericTrial` 方法：

```php
if ($user->onGenericTrial()) {
    // 用户正处于其“通用试用”期内……
}
```


### 延长试用期（Extending Trials）

`extendTrial` 方法允许你在订阅创建之后**延长订阅的试用期**。如果试用期已经结束，并且客户已经开始为该订阅付费，你仍然可以为其提供延长的试用期。客户在试用期内所花费的时间将从其下一张发票中扣除：

```php
use App\Models\User;

$subscription = User::find(1)->subscription('default');

// 将试用期设置为从现在起 7 天后结束……
$subscription->extendTrial(
    now()->addDays(7)
);

// 在现有试用期基础上再增加 5 天……
$subscription->extendTrial(
    $subscription->trial_ends_at->addDays(5)
);
```



## 处理 Stripe Webhooks（Handling Stripe Webhooks）

> [!注意]
> 你可以使用 [Stripe CLI](https://stripe.com/docs/stripe-cli) 来帮助在本地开发期间测试 webhooks。

Stripe 可以通过 webhooks 向你的应用程序通知各种事件。默认情况下，Cashier 服务提供者会自动注册一个指向 Cashier webhook 控制器的路由。该控制器将处理所有传入的 webhook 请求。

默认情况下，Cashier 的 webhook 控制器会自动处理**因失败扣款次数过多而被取消的订阅**（由你的 Stripe 设置定义）、客户更新、客户删除、订阅更新以及付款方式更改；不过，正如我们接下来将看到的那样，你可以扩展该控制器来处理任何你需要的 Stripe webhook 事件。

为确保你的应用程序能够处理 Stripe webhooks，请务必在 Stripe 控制面板中配置 webhook URL。默认情况下，Cashier 的 webhook 控制器会响应 `/stripe/webhook` URL 路径。在 Stripe 控制面板中你应当启用的所有 webhook 事件完整列表如下：

- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `customer.updated`
- `customer.deleted`
- `payment_method.automatically_updated`
- `invoice.payment_action_required`
- `invoice.payment_succeeded`

为方便起见，Cashier 提供了一个 `cashier:webhook` Artisan 命令。该命令会在 Stripe 中创建一个 webhook，用于监听 Cashier 所需的所有事件：

```shell
php artisan cashier:webhook
```

默认情况下，创建的 webhook 会指向由 `APP_URL` 环境变量以及 Cashier 自带的 `cashier.webhook` 路由所定义的 URL。如果你希望使用不同的 URL，可以在调用该命令时提供 `--url` 选项：

```shell
php artisan cashier:webhook --url "https://example.com/stripe/webhook"
```



创建的 webhook 将使用与你当前版本的 Cashier 兼容的 Stripe API 版本。如果你希望使用不同的 Stripe 版本，可以提供 `--api-version` 选项：

```shell
php artisan cashier:webhook --api-version="2019-12-03"
```

创建完成后，webhook 将立即处于激活状态。如果你希望先创建 webhook，但在你准备好之前保持其禁用状态，可以在调用该命令时提供 `--disabled` 选项：

```shell
php artisan cashier:webhook --disabled
```

> [!警告]
> 请确保使用 Cashier 自带的 [webhook 签名验证](#verifying-webhook-signatures) 中间件来保护传入的 Stripe webhook 请求。

### Webhook 与 CSRF 保护

由于 Stripe webhook 需要绕过 Laravel 的 [CSRF 保护](/docs/laravel/12.x/csrf)，你应该确保 Laravel 不会尝试为传入的 Stripe webhook 验证 CSRF 令牌。为此，你应在应用的 `bootstrap/app.php` 文件中将 `stripe/*` 排除在 CSRF 保护之外：

```php
->withMiddleware(function (Middleware $middleware) {
    $middleware->validateCsrfTokens(except: [
        'stripe/*',
    ]);
})
```

### 定义 Webhook 事件处理器

Cashier 会自动处理因扣款失败导致的订阅取消以及其他常见的 Stripe webhook 事件。然而，如果你还有其他想要处理的 webhook 事件，你可以通过监听 Cashier 分发的以下事件来实现：
-   `Laravel\Cashier\Events\WebhookReceived`
-   `Laravel\Cashier\Events\WebhookHandled`
这两个事件都包含 Stripe webhook 的完整载荷（payload）。例如，如果你希望处理 `invoice.payment_succeeded` webhook，你可以注册一个 [监听器](/docs/laravel/12.x/events#defining-listeners) 来处理该事件：

```php
<?php

namespace App\Listeners;

use Laravel\Cashier\Events\WebhookReceived;

class StripeEventListener
{
    /**
     * 处理接收到的 Stripe webhook。
     */
    public function handle(WebhookReceived $event): void
    {
        if ($event->payload['type'] === 'invoice.payment_succeeded') {
            // 处理传入的事件……
        }
    }
}
```



### 验证 Webhook 签名

为了保护你的 webhook，你可以使用 [Stripe 的 webhook 签名](https://stripe.com/docs/webhooks/signatures)。为方便起见，Cashier 自动包含了一个中间件，用于验证传入的 Stripe webhook 请求是否有效。

要启用 webhook 验证，请确保在你应用的 `.env` 文件中设置了 `STRIPE_WEBHOOK_SECRET` 环境变量。该 webhook 的 `secret` 可以从你的 Stripe 账户控制面板中获取。

## 单次收费

### 简单收费

如果你希望对某个客户进行一次性收费，可以在一个可计费模型实例上使用 `charge` 方法。你需要将一个[支付方式标识符](#payment-methods-for-single-charges)作为第二个参数传递给 `charge` 方法：

```php
use Illuminate\Http\Request;

Route::post('/purchase', function (Request $request) {
    $stripeCharge = $request->user()->charge(
        100, $request->paymentMethodId
    );

    // ...
});
```

`charge` 方法接受一个数组作为第三个参数，这允许你将任何你希望的选项传递给底层的 Stripe 收费创建过程。关于创建收费时可用选项的更多信息，可以在 [Stripe 文档](https://stripe.com/docs/api/charges/create) 中找到：

```php
$user->charge(100, $paymentMethod, [
    'custom_option' => $value,
]);
```

你也可以在没有底层客户或用户的情况下使用 `charge` 方法。为此，可以在你应用的可计费模型的新实例上调用 `charge` 方法：

```php
use App\Models\User;

$stripeCharge = (new User)->charge(100, $paymentMethod);
```

如果收费失败，`charge` 方法将抛出一个异常。如果收费成功，该方法将返回一个 `Laravel\Cashier\Payment` 实例：

```php
try {
    $payment = $user->charge(100, $paymentMethod);
} catch (Exception $e) {
    // ...
}
```

> [!警告]
> `charge` 方法接收的支付金额应使用你应用所用货币的最小单位。例如，如果客户使用美元（USD）支付，则金额应以“美分”为单位指定。



### 使用发票收费

有时你可能需要进行一次性收费，并向客户提供一份 PDF 发票。`invoicePrice` 方法正是用于此目的的。例如，我们可以为客户就五件新衬衫开具发票：

```php
$user->invoicePrice('price_tshirt', 5);
```

该发票将立即使用用户的默认支付方式进行扣款。`invoicePrice` 方法还接受一个数组作为第三个参数。该数组包含发票项目的计费选项。该方法接受的第四个参数同样是一个数组，用于包含发票本身的计费选项：

```php
$user->invoicePrice('price_tshirt', 5, [
    'discounts' => [
        ['coupon' => 'SUMMER21SALE']
    ],
], [
    'default_tax_rates' => ['txr_id'],
]);
```

与 `invoicePrice` 类似，你可以使用 `tabPrice` 方法，通过将多个项目（每张发票最多 250 个项目）添加到客户的“账单标签（tab）”中，然后再向客户开具发票，从而创建一次性收费。例如，我们可以为客户就五件衬衫和两个杯子开具发票：

```php
$user->tabPrice('price_tshirt', 5);
$user->tabPrice('price_mug', 2);
$user->invoice();
```

另外，你也可以使用 `invoiceFor` 方法，对客户的默认支付方式进行一次“单次”收费：

```php
$user->invoiceFor('One Time Fee', 500);
```

尽管 `invoiceFor` 方法可供你使用，但建议你使用带有预定义价格的 `invoicePrice` 和 `tabPrice` 方法。这样做可以让你在 Stripe 控制面板中获得更好的分析和数据，从而按产品维度查看你的销售情况。

> [!警告]
> `invoice`、`invoicePrice` 以及 `invoiceFor` 方法都会创建一个 Stripe 发票，该发票会在扣款失败时自动重试。如果你不希望发票在扣款失败后进行重试，则需要在首次扣款失败后，使用 Stripe API 将该发票关闭。



### 创建 Payment Intents

你可以在一个可计费模型实例上调用 `pay` 方法来创建一个新的 Stripe payment intent。调用该方法将创建一个 payment intent，并将其封装在一个 `Laravel\Cashier\Payment` 实例中：

```php
use Illuminate\Http\Request;

Route::post('/pay', function (Request $request) {
    $payment = $request->user()->pay(
        $request->get('amount')
    );

    return $payment->client_secret;
});
```

在创建 payment intent 之后，你可以将 client secret 返回给应用的前端，以便用户在浏览器中完成支付。有关使用 Stripe payment intents 构建完整支付流程的更多信息，请参阅 [Stripe 文档](https://stripe.com/docs/payments/accept-a-payment?platform=web)。

当使用 `pay` 方法时，在你的 Stripe 控制面板中启用的默认支付方式将可供客户使用。或者，如果你只希望允许某些特定的支付方式，可以使用 `payWith` 方法：

```php
use Illuminate\Http\Request;

Route::post('/pay', function (Request $request) {
    $payment = $request->user()->payWith(
        $request->get('amount'), ['card', 'bancontact']
    );

    return $payment->client_secret;
});
```

> [!警告]
> `pay` 和 `payWith` 方法接收的支付金额应使用你应用所用货币的最小单位。例如，如果客户使用美元（USD）支付，则金额应以“美分”为单位指定。


### 退款收费

如果你需要对某个 Stripe 收费进行退款，可以使用 `refund` 方法。该方法将 Stripe 的 [payment intent ID](#payment-methods-for-single-charges) 作为第一个参数：

```php
$payment = $user->charge(100, $paymentMethodId);

$user->refund($payment->id);
```



## 发票

### 获取发票

你可以使用 `invoices` 方法轻松获取某个可计费模型的发票数组。`invoices` 方法返回一个由 `Laravel\Cashier\Invoice` 实例组成的集合：

```php
$invoices = $user->invoices();
```

如果你希望在结果中包含待处理（pending）的发票，可以使用 `invoicesIncludingPending` 方法：

```php
$invoices = $user->invoicesIncludingPending();
```

你可以使用 `findInvoice` 方法，通过发票 ID 获取一张指定的发票：

```php
$invoice = $user->findInvoice($invoiceId);
```

#### 显示发票信息

在列出客户的发票时，你可以使用发票实例提供的方法来显示相关的发票信息。例如，你可能希望在一个表格中列出所有发票，并允许用户轻松下载其中任意一张：

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

### 即将到来的发票

要获取某个客户的即将生成的发票，可以使用 `upcomingInvoice` 方法：

```php
$invoice = $user->upcomingInvoice();
```

同样地，如果客户拥有多个订阅，你也可以获取某个特定订阅的即将生成的发票：

```php
$invoice = $user->subscription('default')->upcomingInvoice();
```

### 预览订阅发票

通过使用 `previewInvoice` 方法，你可以在进行价格更改之前预览发票。这将使你能够确定在进行某个价格变更时，客户的发票将会是什么样子：

```php
$invoice = $user->subscription('default')->previewInvoice('price_yearly');
```



你可以向 `previewInvoice` 方法传入一个价格数组，以便预览包含多个新价格的发票：

```php
$invoice = $user->subscription('default')->previewInvoice(['price_yearly', 'price_metered']);
```

### 生成发票 PDF（Generating Invoice PDFs）

在生成发票 PDF 之前，你应该使用 Composer 安装 Dompdf 库，它是 Cashier 默认使用的发票渲染器：

```shell
composer require dompdf/dompdf
```

在路由或控制器中，你可以使用 `downloadInvoice` 方法来生成指定发票的 PDF 下载。该方法会自动生成下载发票所需的正确 HTTP 响应：

```php
use Illuminate\Http\Request;

Route::get('/user/invoice/{invoice}', function (Request $request, string $invoiceId) {
    return $request->user()->downloadInvoice($invoiceId);
});
```

默认情况下，发票上的所有数据都来源于 Stripe 中存储的客户和发票数据。文件名基于你的 `app.name` 配置值。不过，你可以通过向 `downloadInvoice` 方法传入第二个参数（一个数组）来自定义其中的一些数据。该数组允许你自定义诸如公司信息和产品详情等内容：

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

`downloadInvoice` 方法还允许通过其第三个参数指定自定义的文件名。该文件名会自动添加 `.pdf` 后缀：

```php
return $request->user()->downloadInvoice($invoiceId, [], 'my-invoice');
```


#### 自定义发票渲染器

Cashier 也支持使用自定义的发票渲染器。默认情况下，Cashier 使用 `DompdfInvoiceRenderer` 实现，它利用 [dompdf](https://github.com/dompdf/dompdf) PHP 库来生成 Cashier 的发票。不过，你可以通过实现 `Laravel\Cashier\Contracts\InvoiceRenderer` 接口来使用任何你想要的渲染器。例如，你可能希望通过调用第三方 PDF 渲染服务的 API 来生成发票 PDF：

```php
use Illuminate\Support\Facades\Http;
use Laravel\Cashier\Contracts\InvoiceRenderer;
use Laravel\Cashier\Invoice;

class ApiInvoiceRenderer implements InvoiceRenderer
{
    /**
     * 渲染给定的发票并返回原始的 PDF 字节数据。
     */
    public function render(Invoice $invoice, array $data = [], array $options = []): string
    {
        $html = $invoice->view($data)->render();

        return Http::get('https://example.com/html-to-pdf', ['html' => $html])->get()->body();
    }
}
```

一旦你实现了发票渲染器契约，就应该在应用的 `config/cashier.php` 配置文件中更新 `cashier.invoices.renderer` 配置值。该配置值应设置为你自定义渲染器实现的类名。

## 结账（Checkout）

Cashier Stripe 还提供了对 [Stripe Checkout](https://stripe.com/payments/checkout) 的支持。Stripe Checkout 通过提供一个预构建、托管的支付页面，消除了实现自定义收款页面的复杂性。

以下文档包含了如何开始在 Cashier 中使用 Stripe Checkout 的相关信息。要了解更多关于 Stripe Checkout 的内容，你还可以参考 [Stripe 自身关于 Checkout 的文档](https://stripe.com/docs/payments/checkout)。

### 产品结账（Product Checkouts）





你可以通过在一个可计费模型（billable model）上使用 `checkout` 方法，对已经在 Stripe 仪表板中创建的现有产品执行结账操作。`checkout` 方法会启动一个新的 Stripe Checkout 会话。默认情况下，你需要传入一个 Stripe 的 Price ID：

```php
use Illuminate\Http\Request;

Route::get('/product-checkout', function (Request $request) {
    return $request->user()->checkout('price_tshirt');
});
```

如有需要，你也可以指定产品数量：

```php
use Illuminate\Http\Request;

Route::get('/product-checkout', function (Request $request) {
    return $request->user()->checkout(['price_tshirt' => 15]);
});
```

当客户访问该路由时，他们将被重定向到 Stripe 的 Checkout 页面。默认情况下，当用户成功完成或取消购买时，他们将被重定向到你的 `home` 路由位置，但你也可以通过 `success_url` 和 `cancel_url` 选项来指定自定义的回调 URL：

```php
use Illuminate\Http\Request;

Route::get('/product-checkout', function (Request $request) {
    return $request->user()->checkout(['price_tshirt' => 1], [
        'success_url' => route('your-success-route'),
        'cancel_url' => route('your-cancel-route'),
    ]);
});
```

在定义 `success_url` 结账选项时，你可以指示 Stripe 在调用你的 URL 时，将 Checkout 会话 ID 作为查询字符串参数附加到 URL 中。为此，请在你的 `success_url` 查询字符串中添加字面字符串 `{CHECKOUT_SESSION_ID}`。Stripe 会将该占位符替换为实际的 Checkout 会话 ID：

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



#### 促销码（Promotion Codes）

默认情况下，Stripe Checkout 不允许使用[用户可兑换的促销码](https://stripe.com/docs/billing/subscriptions/discounts/codes)。幸运的是，有一种简单的方法可以为你的 Checkout 页面启用它们。为此，你可以调用 `allowPromotionCodes` 方法：

```php
use Illuminate\Http\Request;

Route::get('/product-checkout', function (Request $request) {
    return $request->user()
        ->allowPromotionCodes()
        ->checkout('price_tshirt');
});
```

### 单次收费结账（Single Charge Checkouts）

你也可以对一个尚未在 Stripe 仪表板中创建的临时产品执行一次简单的收费。为此，你可以在可计费模型（billable model）上使用 `checkoutCharge` 方法，并向其传入一个可收费金额、一个产品名称，以及一个可选的数量。当客户访问该路由时，他们将被重定向到 Stripe 的 Checkout 页面：

```php
use Illuminate\Http\Request;

Route::get('/charge-checkout', function (Request $request) {
    return $request->user()->checkoutCharge(1200, 'T-Shirt', 5);
});
```

> [!警告]
> 当使用 `checkoutCharge` 方法时，Stripe 将始终在你的 Stripe 仪表板中创建一个新的产品和价格。因此，我们建议你提前在 Stripe 仪表板中创建产品，并改用 `checkout` 方法。

### 订阅结账（Subscription Checkouts）

> [!警告]
> 使用 Stripe Checkout 进行订阅时，你需要在 Stripe 仪表板中启用 `customer.subscription.created` webhook。该 webhook 会在你的数据库中创建订阅记录，并存储所有相关的订阅项目。

你也可以使用 Stripe Checkout 来发起订阅。在使用 Cashier 的订阅构建器方法定义好订阅之后，你可以调用 `checkout` 方法。当客户访问该路由时，他们将被重定向到 Stripe 的 Checkout 页面：

```php
use Illuminate\Http\Request;

Route::get('/subscription-checkout', function (Request $request) {
    return $request->user()
        ->newSubscription('default', 'price_monthly')
        ->checkout();
});
```



正如产品结账一样，你也可以自定义成功和取消的 URL：

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

当然，你也可以为订阅结账启用促销码：

```php
use Illuminate\Http\Request;

Route::get('/subscription-checkout', function (Request $request) {
    return $request->user()
        ->newSubscription('default', 'price_monthly')
        ->allowPromotionCodes()
        ->checkout();
});
```

> [!警告]
> 不幸的是，Stripe Checkout 在启动订阅时并不支持所有的订阅计费选项。在订阅构建器上使用 `anchorBillingCycleOn` 方法、设置按比例计费行为（proration behavior），或设置支付行为（payment behavior），在 Stripe Checkout 会话期间都不会产生任何效果。请查阅 [Stripe Checkout Session API 文档](https://stripe.com/docs/api/checkout/sessions/create)，以了解哪些参数是可用的。

#### Stripe Checkout 与试用期（Trial Periods）

当然，在使用 Stripe Checkout 完成的订阅中，你可以在构建订阅时定义一个试用期：

```php
$checkout = Auth::user()->newSubscription('default', 'price_monthly')
    ->trialDays(3)
    ->checkout();
```

然而，试用期必须至少为 48 小时，这是 Stripe Checkout 所支持的最短试用时间。

#### 订阅与 Webhooks

请记住，Stripe 和 Cashier 是通过 webhooks 来更新订阅状态的，因此在客户输入付款信息并返回应用程序时，订阅有可能尚未处于激活状态。为处理这种情况，你可能希望显示一条消息，告知用户他们的付款或订阅正在等待处理中。



### 收集税号（Collecting Tax IDs）

Checkout 也支持收集客户的税号。要在结账会话中启用此功能，请在创建会话时调用 `collectTaxIds` 方法：

```php
$checkout = $user->collectTaxIds()->checkout('price_tshirt');
```

当调用该方法时，客户将看到一个新的复选框，用于指示他们是否以公司名义进行购买。如果是，他们将有机会提供自己的税号。

> [!警告]
> 如果你已经在应用的服务提供者中配置了[自动税费计算](#tax-configuration)，那么该功能将会自动启用，而无需调用 `collectTaxIds` 方法。

### 游客结账（Guest Checkouts）

通过使用 `Checkout::guest` 方法，你可以为应用中没有“账户”的游客发起结账会话：

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

与为现有用户创建结账会话类似，你也可以使用 `Laravel\Cashier\CheckoutBuilder` 实例上提供的其他方法来自定义游客结账会话：

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

在游客结账完成之后，Stripe 可以发送一个 `checkout.session.completed` webhook 事件，因此请确保你已经[配置 Stripe webhook](https://dashboard.stripe.com/webhooks)，以便将该事件实际发送到你的应用中。一旦在 Stripe 仪表板中启用了该 webhook，你就可以[使用 Cashier 处理该 webhook](#handling-stripe-webhooks)。Webhook 载荷中包含的对象将是一个 [checkout 对象](https://stripe.com/docs/api/checkout/sessions/object)，你可以检查该对象以完成客户的订单。



## 处理失败的支付（Handling Failed Payments）

有时，订阅（subscription）或单次扣费（single charge）的支付可能会失败。当这种情况发生时，Cashier 会抛出 `Laravel\Cashier\Exceptions\IncompletePayment` 异常，用来告知你支付失败这一事件。在捕获（catch）该异常后，你有两种继续处理的方式（options on how to proceed）。

首先，你可以将用户重定向（redirect）到 Cashier 自带的专用支付确认页面（payment confirmation page）。该页面已经由 Cashier 的 Service Provider（服务提供者）注册了一个命名路由（named route）。因此，你可以捕获 `IncompletePayment` 异常，并将用户重定向到支付确认页面，如下所示：

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

在支付确认页面中，用户将被提示重新输入他们的信用卡信息，并完成 Stripe 可能要求的其他额外操作，例如 **“3D Secure”** 支付验证（confirmation）。支付确认完成后，用户会被重定向到上面通过 `redirect` 参数指定的 URL。

在重定向（redirection）后，URL 中会被附加 `message`（字符串 / string）和 `success`（整数 / integer）这两个查询字符串变量（query string variables）。

当前，该支付确认页面支持以下支付方式类型（payment method types）：

<div class="content-list" markdown="1">

-   信用卡（Credit Cards）
-   支付宝（Alipay）
-   Bancontact
-   BECS 直接借记（BECS Direct Debit）
-   EPS
-   Giropay
-   iDEAL
-   SEPA 直接借记（SEPA Direct Debit）

</div>

另外（Alternatively），你也可以让 Stripe 为你自动处理支付确认。在这种情况下，你可以在 Stripe Dashboard（仪表盘）中启用[Stripe 的自动账单邮件](https://dashboard.stripe.com/account/billing/automatic)。

不过，即便捕获到了 `IncompletePayment` 异常，你仍然应该告知用户他们将会收到一封包含后续支付确认指引（further payment confirmation instructions）的邮件（email）。并提醒用户查收邮件以完成支付。



对于使用 `Billable` trait 的模型，以下方法可能会抛出支付异常（payment exceptions）：`charge`、`invoiceFor` 以及 `invoice`。在操作订阅（subscriptions）时，`SubscriptionBuilder` 中的 `create` 方法，以及 `Subscription`、`SubscriptionItem` 和 `SubscriptionItem` 模型中的 `incrementAndInvoice`、`swapAndInvoice` 方法，都可能会抛出未完成支付（incomplete payment）异常。

判断现有订阅（existing subscription）是否存在未完成支付，可以通过 Billable 模型或订阅实例（subscription instance）上的 `hasIncompletePayment` 方法来完成：

```php
if ($user->hasIncompletePayment('default')) {
    // ...
}

if ($user->subscription('default')->hasIncompletePayment()) {
    // ...
}
```

你可以通过检查异常实例（exception instance）上的 `payment` 属性，来获取未完成支付的具体状态（specific status）：

```php
use Laravel\Cashier\Exceptions\IncompletePayment;

try {
    $user->charge(1000, 'pm_card_threeDSecure2Required');
} catch (IncompletePayment $exception) {
    // 获取 Payment Intent（支付意图）状态……
    $exception->payment->status;

    // 检查特定条件……
    if ($exception->payment->requiresPaymentMethod()) {
        // ...
    } elseif ($exception->payment->requiresConfirmation()) {
        // ...
    }
}
```

### 确认支付（Confirming Payments）

某些支付方式（payment methods）在确认支付时需要额外的数据（additional data）。例如，SEPA 支付方式在支付流程中需要额外的 **“mandate”（授权委托）** 数据。你可以使用 `withPaymentConfirmationOptions` 方法将这些数据提供给 Cashier：

```php
$subscription->withPaymentConfirmationOptions([
    'mandate_data' => '...',
])->swap('price_xxx');
```

你可以查阅 [Stripe API 文档](https://stripe.com/docs/api/payment_intents/confirm) 来了解支付确认时接受的所有可用选项（options accepted when confirming payments）。

## 强客户身份验证（Strong Customer Authentication）

如果你的业务（business）或某位客户（customers）位于欧洲（Europe），你需要遵守欧盟（EU）的 **强客户身份验证（SCA）** 法规。这些法规由欧盟于 2019 年 9 月实施（imposed in September 2019），旨在防止支付欺诈（payment fraud）。幸运的是，Stripe 和 Cashier 已经为构建符合 SCA 规范（SCA compliant）的应用做好了准备。

> [!警告]
> 在开始之前，请先查阅 [Stripe 关于 PSD2 和 SCA 的指南](https://stripe.com/guides/strong-customer-authentication)，以及他们关于[新 SCA API 的文档](https://stripe.com/docs/strong-customer-authentication)。



### 需要额外确认的支付

根据 SCA（强客户身份认证）法规，支付通常需要额外的验证才能确认并完成处理。当发生这种情况时，Cashier 会抛出 `Laravel\Cashier\Exceptions\IncompletePayment` 异常，用于告知需要额外的验证。有关如何处理这些异常的更多信息，可以在[处理失败支付](#handling-failed-payments)的文档中找到。

Stripe 或 Cashier 提供的支付确认界面可能会针对特定银行或发卡机构的支付流程进行定制，并且可能包含额外的卡片确认、临时小额扣费、独立的设备认证或其他形式的验证。

#### Incomplete（未完成）和 Past Due（逾期）状态

当支付需要额外确认时，订阅将保持在 `incomplete`（未完成）或 `past_due`（逾期）状态，这由数据库中的 `stripe_status` 字段列指示。Cashier 会在支付确认完成后自动激活客户的订阅，前提是 Stripe 通过 webhook 通知应用支付已完成。

有关 `incomplete` 和 `past_due` 状态的更多信息，请参考[我们关于这些状态的额外文档](#incomplete-and-past-due-status)。

### 站外支付通知

由于 SCA 法规要求客户即使在订阅处于激活状态期间，也可能需要不定期验证支付信息，因此 Cashier 可以在需要站外支付确认时向客户发送通知。例如，这种情况可能发生在订阅续费时。可以通过将环境变量 `CASHIER_PAYMENT_NOTIFICATION` 设置为一个通知类来启用 Cashier 的支付通知功能。默认情况下，该通知功能是禁用的。当然，Cashier 也提供了一个可以直接使用的通知类，但如果需要，你也可以自定义通知类：

```ini
CASHIER_PAYMENT_NOTIFICATION=Laravel\Cashier\Notifications\ConfirmPayment
```



为了确保站外支付确认通知能够成功送达，请确认你的应用已[配置 Stripe Webhooks](#handling-stripe-webhooks)，并且在 Stripe 控制面板中启用了 `invoice.payment_action_required` 这个 webhook 事件。此外，你的 `Billable` 模型也需要使用 Laravel 的 `Illuminate\Notifications\Notifiable` Trait。

> [!警告]
> 即使客户是在手动进行需要额外确认的支付时，通知也会被发送。遗憾的是，Stripe 无法得知该支付是手动完成还是“站外（off-session）”完成的。不过，如果客户在已经确认支付后访问支付页面，他们只会看到“支付成功（Payment Successful）”的消息。系统不会允许客户意外确认同一笔支付两次，从而避免产生第二次扣费的意外重复扣款。

## Stripe SDK

Cashier 的许多对象都是对 Stripe SDK 对象的封装（Wrapper）。如果你希望直接操作 Stripe 对象，你可以使用 `asStripe` 方法方便地获取它们：

```php
$stripeSubscription = $subscription->asStripeSubscription();

$stripeSubscription->application_fee_percent = 5;

$stripeSubscription->save();
```

你也可以使用 `updateStripeSubscription` 方法直接更新 Stripe 订阅：

```php
$subscription->updateStripeSubscription(['application_fee_percent' => 5]);
```

如果你希望直接使用 `Stripe\StripeClient` 客户端，你可以调用 `Cashier` 类上的 `stripe` 方法。例如，你可以使用这个方法获取 `StripeClient` 实例，并从你的 Stripe 账户中检索价格列表：

```php
use Laravel\Cashier\Cashier;

$prices = Cashier::stripe()->prices->all();
```

## 测试

在测试使用 Cashier 的应用时，你可以 Mock 发送到 Stripe API 的真实 HTTP 请求，但这需要你部分重新实现 Cashier 自身的行为逻辑。因此，我们建议在测试中允许直接请求真实的 Stripe API。虽然这样会更慢，但能够让你更有信心地确认应用是否正常工作，同时你也可以将这些较慢的测试放入独立的 Pest / PHPUnit 测试分组中。



在测试时，请记住 Cashier 本身已经拥有非常完善的测试套件，因此你应该只专注于测试你自己应用中的订阅和支付流程，而不是测试 Cashier 的所有底层行为。

要开始测试，请将 **测试（testing）版本** 的 Stripe 密钥添加到你的 `phpunit.xml` 文件中：

```xml
<env name="STRIPE_SECRET" value="sk_test_<your-key>"/>
```

现在，在测试环境中与 Cashier 进行交互时，它将会向 Stripe 的测试环境发送真实的 API 请求。为了方便测试，你应该在 Stripe 测试账户中预先填充（Pre-fill）测试所需的订阅（Subscriptions）或价格（Prices）。

> [!注意]
> 为了测试多种不同的账单场景，例如信用卡拒付（denials）或支付失败（failures），你可以使用 Stripe 提供的大量[测试卡号和 Token](#) 进行测试。
