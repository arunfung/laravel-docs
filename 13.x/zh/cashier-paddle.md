# Laravel Cashier (Paddle)

- [简介](#introduction)
- [升级 Cashier](#upgrading-cashier)
- [安装](#installation)
    - [Paddle 沙盒](#paddle-sandbox)
- [配置](#configuration)
    - [可计费模型](#billable-model)
    - [API 密钥](#api-keys)
    - [Paddle JS](#paddle-js)
    - [货币配置](#currency-configuration)
    - [覆盖默认模型](#overriding-default-models)
- [快速入门](#quickstart)
    - [销售产品](#quickstart-selling-products)
    - [销售订阅](#quickstart-selling-subscriptions)
- [结账会话](#checkout-sessions)
    - [覆盖式结账](#overlay-checkout)
    - [嵌入式结账](#inline-checkout)
    - [游客结账](#guest-checkouts)
- [价格预览](#price-previews)
    - [客户价格预览](#customer-price-previews)
    - [折扣](#price-discounts)
- [客户](#customers)
    - [客户默认值](#customer-defaults)
    - [获取客户](#retrieving-customers)
    - [创建客户](#creating-customers)
- [订阅](#subscriptions)
    - [创建订阅](#creating-subscriptions)
    - [检查订阅状态](#checking-subscription-status)
    - [订阅单次收费](#subscription-single-charges)
    - [更新支付信息](#updating-payment-information)
    - [更改方案](#changing-plans)
    - [订阅数量](#subscription-quantity)
    - [多产品订阅](#subscriptions-with-multiple-products)
    - [多个订阅](#multiple-subscriptions)
    - [暂停订阅](#pausing-subscriptions)
    - [取消订阅](#canceling-subscriptions)
- [订阅试用](#subscription-trials)
    - [预先提供支付方式](#with-payment-method-up-front)
    - [不预先提供支付方式](#without-payment-method-up-front)
    - [延长或激活试用](#extend-or-activate-a-trial)
- [处理 Paddle Webhook](#handling-paddle-webhooks)
    - [定义 Webhook 事件处理器](#defining-webhook-event-handlers)
    - [验证 Webhook 签名](#verifying-webhook-signatures)
- [单次收费](#single-charges)
    - [产品收费](#charging-for-products)
    - [交易退款](#refunding-transactions)
    - [交易贷记](#crediting-transactions)
- [交易](#transactions)
    - [过往与即将进行的付款](#past-and-upcoming-payments)
- [测试](#testing)

<a name="introduction"></a>
## 简介

> [!WARNING]
> 本文档介绍 Cashier Paddle 2.x 与 Paddle Billing 的集成。如果你仍在使用 Paddle Classic，应使用 [Cashier Paddle 1.x](https://github.com/laravel/cashier-paddle/tree/1.x)。

[Laravel Cashier Paddle](https://github.com/laravel/cashier-paddle) 为 [Paddle](https://paddle.com) 的订阅计费服务提供清晰、流畅的接口，替你处理几乎所有繁琐的订阅计费样板代码。除了基本的订阅管理，Cashier 还支持切换订阅、订阅「数量」、暂停订阅、取消订阅后的宽限期等功能。

深入了解 Cashier Paddle 之前，建议先阅读 Paddle 的[概念指南](https://developer.paddle.com/concepts/overview)和 [API 文档](https://developer.paddle.com/api-reference/overview)。

<a name="upgrading-cashier"></a>
## 升级 Cashier

升级到新版本的 Cashier 时，请务必仔细阅读[升级指南](https://github.com/laravel/cashier-paddle/blob/master/UPGRADE.md)。

<a name="installation"></a>
## 安装

首先，使用 Composer 包管理器安装适用于 Paddle 的 Cashier 包：

```shell
composer require laravel/cashier-paddle
```

接下来，使用 `vendor:publish` Artisan 命令发布 Cashier 的迁移文件：

```shell
php artisan vendor:publish --tag="cashier-migrations"
```

然后，运行应用的数据库迁移。Cashier 的迁移会创建 `customers` 表，以及用于存储客户订阅信息的 `subscriptions` 和 `subscription_items` 表。最后，还会创建 `transactions` 表，存储与客户关联的所有 Paddle 交易记录：

```shell
php artisan migrate
```

> [!WARNING]
> 为确保 Cashier 正确处理所有 Paddle 事件，请记得[配置 Cashier 的 Webhook 处理](#handling-paddle-webhooks)。

<a name="paddle-sandbox"></a>
### Paddle 沙盒

在本地和预发布环境开发时，应[注册 Paddle Sandbox 账户](https://sandbox-login.paddle.com/signup)。该账户提供沙盒环境，让你无需实际支付即可开发和测试应用。你可以使用 Paddle 的[测试卡号](https://developer.paddle.com/concepts/payment-methods/credit-debit-card#test-payment-method)模拟各种支付场景。

使用 Paddle 沙盒环境时，应在应用的 `.env` 文件中将 `PADDLE_SANDBOX` 环境变量设置为 `true`：

```ini
PADDLE_SANDBOX=true
```

完成应用开发后，你可以[申请 Paddle 商家账户](https://paddle.com)。应用正式上线前，Paddle 需要审核并批准应用的域名。

<a name="configuration"></a>
## 配置

<a name="billable-model"></a>
### 可计费模型

使用 Cashier 之前，必须在用户模型的定义中添加 `Billable` trait。该 trait 提供多种方法，让你执行创建订阅、更新支付方式信息等常见计费任务：

```php
use Laravel\Paddle\Billable;

class User extends Authenticatable
{
    use Billable;
}
```

如果你有不是用户的可计费实体，也可以向这些类添加该 trait：

```php
use Illuminate\Database\Eloquent\Model;
use Laravel\Paddle\Billable;

class Team extends Model
{
    use Billable;
}
```

<a name="api-keys"></a>
### API 密钥

接下来，在应用的 `.env` 文件中配置 Paddle 密钥。你可以从 Paddle 控制面板获取 API 密钥：

```ini
PADDLE_CLIENT_SIDE_TOKEN=your-paddle-client-side-token
PADDLE_API_KEY=your-paddle-api-key
PADDLE_RETAIN_KEY=your-paddle-retain-key
PADDLE_WEBHOOK_SECRET="your-paddle-webhook-secret"
PADDLE_SANDBOX=true
```

使用 [Paddle 沙盒环境](#paddle-sandbox)时，应将 `PADDLE_SANDBOX` 环境变量设置为 `true`。如果将应用部署到生产环境并使用 Paddle 正式商家环境，则应将其设置为 `false`。

`PADDLE_RETAIN_KEY` 是可选项，仅在使用 Paddle 的 [Retain](https://developer.paddle.com/concepts/retain/overview) 功能时需要设置。

<a name="paddle-js"></a>
### Paddle JS

Paddle 使用自己的 JavaScript 库启动结账组件。你可以在应用布局的 `</head>` 结束标签前放置 `@paddleJS` Blade 指令，以加载该库：

```blade
<head>
    ...

    @paddleJS
</head>
```

<a name="currency-configuration"></a>
### 货币配置

你可以指定语言区域，用于格式化发票上显示的金额。Cashier 在内部使用 [PHP 的 `NumberFormatter` 类](https://www.php.net/manual/en/class.numberformatter.php)设置货币的语言区域：

```ini
CASHIER_CURRENCY_LOCALE=nl_BE
```

> [!WARNING]
> 要使用 `en` 之外的语言区域，请确保服务器已安装并配置 `ext-intl` PHP 扩展。

<a name="overriding-default-models"></a>
### 覆盖默认模型

你可以定义自己的模型并继承相应的 Cashier 模型，来扩展 Cashier 内部使用的模型：

```php
use Laravel\Paddle\Subscription as CashierSubscription;

class Subscription extends CashierSubscription
{
    // ...
}
```

定义模型后，可以通过 `Laravel\Paddle\Cashier` 类让 Cashier 使用自定义模型。通常应在应用的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中完成配置：

```php
use App\Models\Cashier\Subscription;
use App\Models\Cashier\Transaction;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Cashier::useSubscriptionModel(Subscription::class);
    Cashier::useTransactionModel(Transaction::class);
}
```

<a name="quickstart"></a>
## 快速入门

<a name="quickstart-selling-products"></a>
### 销售产品

> [!NOTE]
> 使用 Paddle Checkout 之前，应先在 Paddle 控制面板中定义具有固定价格的产品，并[配置 Paddle 的 Webhook 处理](#handling-paddle-webhooks)。

为应用提供产品销售和订阅计费功能可能让人望而却步，但借助 Cashier 和 [Paddle Checkout Overlay](https://developer.paddle.com/concepts/sell/overlay-checkout)，你可以轻松构建现代、可靠的支付集成。

对于非循环、仅收费一次的产品，我们使用 Cashier 和 Paddle Checkout Overlay 向客户收费，让客户填写支付信息并确认购买。通过 Checkout Overlay 完成付款后，客户会被重定向到应用中指定的成功页面 URL：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $request->user()->checkout('pri_deluxe_album')
        ->returnTo(route('dashboard'));

    return view('buy', ['checkout' => $checkout]);
})->name('checkout');
```

如上例所示，我们使用 Cashier 提供的 `checkout` 方法创建结账对象，根据给定的「价格标识符」向客户展示 Paddle Checkout Overlay。在 Paddle 中，「价格」指的是[为特定产品定义的价格](https://developer.paddle.com/build/products/create-products-prices)。

必要时，`checkout` 方法会自动在 Paddle 中创建客户，并将该客户记录与应用数据库中的相应用户关联。结账会话结束后，客户会被重定向到专门的成功页面，你可以在页面上向客户显示提示信息。

在 `buy` 视图中，我们会放置一个按钮来显示 Checkout Overlay。Cashier Paddle 提供了 `paddle-button` Blade 组件；你也可以[手动渲染覆盖式结账](#manually-rendering-an-overlay-checkout)：

```html
<x-paddle-button :checkout="$checkout" class="px-8 py-4">
    Buy Product
</x-paddle-button>
```

<a name="providing-meta-data-to-paddle-checkout"></a>
#### 向 Paddle Checkout 提供元数据

销售产品时，通常会使用应用自行定义的 `Cart` 和 `Order` 模型来跟踪已完成的订单和已购买的产品。将客户重定向到 Paddle Checkout Overlay 完成购买时，你可能需要提供现有订单的标识符，以便客户返回应用后，将已完成的购买与相应订单关联起来。

为此，你可以向 `checkout` 方法提供一个自定义数据数组。假设用户开始结账时，应用会创建一个待处理的 `Order`。请注意，示例中的 `Cart` 和 `Order` 模型仅用于说明，并非由 Cashier 提供；你可以根据应用需求自行实现：

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

    $checkout = $request->user()->checkout($order->price_ids)
        ->customData(['order_id' => $order->id]);

    return view('billing', ['checkout' => $checkout]);
})->name('checkout');
```

如上例所示，用户开始结账时，我们会将购物车或订单关联的所有 Paddle 价格标识符传给 `checkout` 方法。客户添加商品时，应用负责将商品与「购物车」或订单关联。我们还通过 `customData` 方法将订单 ID 传给 Paddle Checkout Overlay。

客户完成结账后，你可能希望将订单标记为「已完成」。为此，可以监听 Paddle 发送并由 Cashier 以事件形式触发的 Webhook，将订单信息存入数据库。

首先，监听 Cashier 分发的 `TransactionCompleted` 事件。通常应在应用的 `AppServiceProvider` 类的 `boot` 方法中注册事件监听器：

```php
use App\Listeners\CompleteOrder;
use Illuminate\Support\Facades\Event;
use Laravel\Paddle\Events\TransactionCompleted;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    Event::listen(TransactionCompleted::class, CompleteOrder::class);
}
```

在此示例中，`CompleteOrder` 监听器可以如下定义：

```php
namespace App\Listeners;

use App\Models\Order;
use Laravel\Paddle\Cashier;
use Laravel\Paddle\Events\TransactionCompleted;

class CompleteOrder
{
    /**
     * 处理传入的 Cashier Webhook 事件。
     */
    public function handle(TransactionCompleted $event): void
    {
        $orderId = $event->payload['data']['custom_data']['order_id'] ?? null;

        $order = Order::findOrFail($orderId);

        $order->update(['status' => 'completed']);
    }
}
```

有关 [`transaction.completed` 事件包含的数据](https://developer.paddle.com/webhooks/transactions/transaction-completed)，请参阅 Paddle 文档。

<a name="quickstart-selling-subscriptions"></a>
### 销售订阅

> [!NOTE]
> 使用 Paddle Checkout 之前，应先在 Paddle 控制面板中定义具有固定价格的产品，并[配置 Paddle 的 Webhook 处理](#handling-paddle-webhooks)。

为应用提供产品销售和订阅计费功能可能让人望而却步，但借助 Cashier 和 [Paddle Checkout Overlay](https://developer.paddle.com/concepts/sell/overlay-checkout)，你可以轻松构建现代、可靠的支付集成。

为了了解如何使用 Cashier 和 Paddle Checkout Overlay 销售订阅，我们以一个简单的订阅服务为例：它提供基础月付方案（`price_basic_monthly`）和年付方案（`price_basic_yearly`），这两个价格可以归在 Paddle 控制面板的「Basic」产品（`pro_basic`）下。此外，该服务还可能提供 Expert 方案，对应产品 `pro_expert`。

首先，看看客户如何订阅服务。客户可能会在应用的定价页面点击 Basic 方案的「订阅」按钮，该按钮会针对所选方案打开 Paddle Checkout Overlay。先通过 `checkout` 方法创建结账会话：

```php
use Illuminate\Http\Request;

Route::get('/subscribe', function (Request $request) {
    $checkout = $request->user()->checkout('price_basic_monthly')
        ->returnTo(route('dashboard'));

    return view('subscribe', ['checkout' => $checkout]);
})->name('subscribe');
```

在 `subscribe` 视图中，我们会放置一个按钮来显示 Checkout Overlay。Cashier Paddle 提供了 `paddle-button` Blade 组件；你也可以[手动渲染覆盖式结账](#manually-rendering-an-overlay-checkout)：

```html
<x-paddle-button :checkout="$checkout" class="px-8 py-4">
    Subscribe
</x-paddle-button>
```

现在，点击 Subscribe 按钮后，客户即可填写支付信息并创建订阅。由于某些支付方式需要几秒钟才能处理完毕，还应[配置 Cashier 的 Webhook 处理](#handling-paddle-webhooks)，以确定订阅何时真正开始。

现在客户已能创建订阅，我们需要限制应用的部分功能，让它们仅对已订阅用户开放。你可以通过 Cashier 的 `Billable` trait 提供的 `subscribed` 方法判断用户当前的订阅状态：

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

为了便于复用，你可以创建一个[中间件](/docs/{{version}}/middleware)，判断传入请求是否来自已订阅用户。定义后，将它分配给路由即可阻止未订阅用户访问：

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
            // 将用户重定向到计费页面，并提示其订阅……
            return redirect('/subscribe');
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

客户可能希望将订阅方案切换为其他产品或「等级」。在上面的示例中，我们希望允许客户将月付订阅改为年付订阅。为此，需要提供一个按钮或类似入口，指向以下路由：

```php
use Illuminate\Http\Request;

Route::put('/subscription/{price}/swap', function (Request $request, $price) {
    $user->subscription()->swap($price); // 本例中的 "$price" 为 "price_basic_yearly"。

    return redirect()->route('dashboard');
})->name('subscription.swap');
```

除了切换方案，还需要允许客户取消订阅。与切换方案类似，提供一个指向以下路由的按钮：

```php
use Illuminate\Http\Request;

Route::put('/subscription/cancel', function (Request $request, $price) {
    $user->subscription()->cancel();

    return redirect()->route('dashboard');
})->name('subscription.cancel');
```

这样，订阅将在计费周期结束时取消。

> [!NOTE]
> 只要配置了 Cashier 的 Webhook 处理，Cashier 就会检查来自 Paddle 的 Webhook，自动保持应用中与 Cashier 相关的数据表同步。例如，通过 Paddle 控制面板取消客户的订阅时，Cashier 会收到相应的 Webhook，并在应用数据库中将订阅标记为「已取消」。

<a name="checkout-sessions"></a>
## 结账会话

大多数向客户收费的操作都通过 Paddle 的[覆盖式结账组件](https://developer.paddle.com/build/checkout/build-overlay-checkout)或[嵌入式结账](https://developer.paddle.com/build/checkout/build-branded-inline-checkout)完成。

使用 Paddle 处理结账支付之前，应在 Paddle 结账设置控制面板中定义应用的[默认支付链接](https://developer.paddle.com/build/transactions/default-payment-link#set-default-link)。

<a name="overlay-checkout"></a>
### 覆盖式结账

显示 Checkout Overlay 组件之前，必须使用 Cashier 生成结账会话。该会话会告知结账组件应执行的计费操作：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $user->checkout('pri_34567')
        ->returnTo(route('dashboard'));

    return view('billing', ['checkout' => $checkout]);
});
```

Cashier 提供了 `paddle-button` [Blade 组件](/docs/{{version}}/blade#components)。你可以将结账会话作为属性传给组件；点击按钮时，Paddle 的结账组件便会显示：

```html
<x-paddle-button :checkout="$checkout" class="px-8 py-4">
    Subscribe
</x-paddle-button>
```

默认情况下，组件会使用 Paddle 的默认样式显示。你可以为组件添加 `data-theme='light'` 等 [Paddle 支持的属性](https://developer.paddle.com/paddlejs/html-data-attributes)来自定义样式：

```html
<x-paddle-button :checkout="$checkout" class="px-8 py-4" data-theme="light">
    Subscribe
</x-paddle-button>
```

Paddle 结账组件以异步方式运行。用户通过组件创建订阅后，Paddle 会向应用发送 Webhook，以便应用正确更新数据库中的订阅状态。因此，务必正确[配置 Webhook](#handling-paddle-webhooks)，以处理来自 Paddle 的状态变更。

> [!WARNING]
> 订阅状态变更后，收到相应 Webhook 的延迟通常很短，但应用仍应考虑到这一延迟：用户完成结账后，订阅可能不会立即可用。

<a name="manually-rendering-an-overlay-checkout"></a>
#### 手动渲染覆盖式结账

你也可以不使用 Laravel 内置的 Blade 组件，手动渲染覆盖式结账。首先，[按照前面的示例](#overlay-checkout)生成结账会话：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $user->checkout('pri_34567')
        ->returnTo(route('dashboard'));

    return view('billing', ['checkout' => $checkout]);
});
```

接下来，可以使用 Paddle.js 初始化结账。在此示例中，我们创建一个带有 `paddle_button` 类的链接。Paddle.js 会检测该类，并在点击链接时显示覆盖式结账：

```blade
<?php
$items = $checkout->getItems();
$customer = $checkout->getCustomer();
$custom = $checkout->getCustomData();
?>

<a
    href='#!'
    class='paddle_button'
    data-items='{!! json_encode($items) !!}'
    @if ($customer) data-customer-id='{{ $customer->paddle_id }}' @endif
    @if ($custom) data-custom-data='{{ json_encode($custom) }}' @endif
    @if ($returnUrl = $checkout->getReturnUrl()) data-success-url='{{ $returnUrl }}' @endif
>
    Buy Product
</a>
```

<a name="inline-checkout"></a>
### 嵌入式结账

如果不想使用 Paddle 的「覆盖式」结账组件，也可以将组件嵌入页面。虽然这种方式不允许调整结账的 HTML 字段，但可以将组件嵌入应用中。

为方便使用嵌入式结账，Cashier 提供了 `paddle-checkout` Blade 组件。首先应[生成结账会话](#overlay-checkout)：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $user->checkout('pri_34567')
        ->returnTo(route('dashboard'));

    return view('billing', ['checkout' => $checkout]);
});
```

然后，将结账会话传给组件的 `checkout` 属性：

```blade
<x-paddle-checkout :checkout="$checkout" class="w-full" />
```

要调整嵌入式结账组件的高度，可以向 Blade 组件传入 `height` 属性：

```blade
<x-paddle-checkout :checkout="$checkout" class="w-full" height="500" />
```

有关嵌入式结账自定义选项的详情，请参阅 Paddle 的[嵌入式结账指南](https://developer.paddle.com/build/checkout/build-branded-inline-checkout)和[可用的结账设置](https://developer.paddle.com/build/checkout/set-up-checkout-default-settings)。

<a name="manually-rendering-an-inline-checkout"></a>
#### 手动渲染嵌入式结账

你也可以不使用 Laravel 内置的 Blade 组件，手动渲染嵌入式结账。首先，[按照前面的示例](#inline-checkout)生成结账会话：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $user->checkout('pri_34567')
        ->returnTo(route('dashboard'));

    return view('billing', ['checkout' => $checkout]);
});
```

接下来，可以使用 Paddle.js 初始化结账。此示例使用 [Alpine.js](https://github.com/alpinejs/alpine) 演示；你可以根据自己的前端技术栈修改示例：

```blade
<?php
$options = $checkout->options();

$options['settings']['frameTarget'] = 'paddle-checkout';
$options['settings']['frameInitialHeight'] = 366;
?>

<div class="paddle-checkout" x-data="{}" x-init="
    Paddle.Checkout.open(@json($options));
">
</div>
```

<a name="guest-checkouts"></a>
### 游客结账

有时，你可能需要为无需在应用中注册账户的用户创建结账会话。为此，可以使用 `guest` 方法：

```php
use Illuminate\Http\Request;
use Laravel\Paddle\Checkout;

Route::get('/buy', function (Request $request) {
    $checkout = Checkout::guest(['pri_34567'])
        ->returnTo(route('home'));

    return view('billing', ['checkout' => $checkout]);
});
```

然后，可以将结账会话传给 [Paddle 按钮](#overlay-checkout)或[嵌入式结账](#inline-checkout) Blade 组件。

<a name="price-previews"></a>
## 价格预览

Paddle 允许按货币自定义价格，也就是为不同国家配置不同价格。Cashier Paddle 的 `previewPrices` 方法可以获取这些价格，该方法接收需要查询的价格 ID：

```php
use Laravel\Paddle\Cashier;

$prices = Cashier::previewPrices(['pri_123', 'pri_456']);
```

货币会根据请求的 IP 地址确定；你也可以指定国家来获取价格：

```php
use Laravel\Paddle\Cashier;

$prices = Cashier::previewPrices(['pri_123', 'pri_456'], ['address' => [
    'country_code' => 'BE',
    'postal_code' => '1234',
]]);
```

获取价格后，可以按需显示：

```blade
<ul>
    @foreach ($prices as $price)
        <li>{{ $price->product['name'] }} - {{ $price->total() }}</li>
    @endforeach
</ul>
```

你也可以分别显示小计和税额：

```blade
<ul>
    @foreach ($prices as $price)
        <li>{{ $price->product['name'] }} - {{ $price->subtotal() }} (+ {{ $price->tax() }} tax)</li>
    @endforeach
</ul>
```

更多信息请参阅 [Paddle 关于价格预览的 API 文档](https://developer.paddle.com/api-reference/pricing-preview/preview-prices)。

<a name="customer-price-previews"></a>
### 客户价格预览

如果用户已经是客户，而你希望显示适用于该客户的价格，可以直接从客户实例获取：

```php
use App\Models\User;

$prices = User::find(1)->previewPrices(['pri_123', 'pri_456']);
```

Cashier 在内部使用用户的客户 ID 获取以其货币计价的价格。例如，美国用户看到美元价格，比利时用户看到欧元价格。如果找不到匹配的货币，则使用产品的默认货币。你可以在 Paddle 控制面板中自定义产品或订阅方案的所有价格。

<a name="price-discounts"></a>
### 折扣

你也可以选择显示折扣后的价格。调用 `previewPrices` 方法时，通过 `discount_id` 选项提供折扣 ID：

```php
use Laravel\Paddle\Cashier;

$prices = Cashier::previewPrices(['pri_123', 'pri_456'], [
    'discount_id' => 'dsc_123'
]);
```

然后显示计算后的价格：

```blade
<ul>
    @foreach ($prices as $price)
        <li>{{ $price->product['name'] }} - {{ $price->total() }}</li>
    @endforeach
</ul>
```

<a name="customers"></a>
## 客户

<a name="customer-defaults"></a>
### 客户默认值

Cashier 允许你为创建结账会话时的客户信息定义默认值。设置后，可以预先填写客户的电子邮件地址和姓名，让客户直接进入结账组件的支付环节。你可以在可计费模型上重写以下方法来设置默认值：

```php
/**
 * 获取要关联到 Paddle 的客户姓名。
 */
public function paddleName(): string|null
{
    return $this->name;
}

/**
 * 获取要关联到 Paddle 的客户电子邮件地址。
 */
public function paddleEmail(): string|null
{
    return $this->email;
}
```

Cashier 中所有生成[结账会话](#checkout-sessions)的操作都会使用这些默认值。

<a name="retrieving-customers"></a>
### 获取客户

你可以使用 `Cashier::findBillable` 方法，通过 Paddle 客户 ID 获取客户。该方法会返回可计费模型的实例：

```php
use Laravel\Paddle\Cashier;

$user = Cashier::findBillable($customerId);
```

<a name="creating-customers"></a>
### 创建客户

有时，你可能希望创建 Paddle 客户，但暂不创建订阅。可以使用 `createAsCustomer` 方法：

```php
$customer = $user->createAsCustomer();
```

该方法返回 `Laravel\Paddle\Customer` 实例。在 Paddle 中创建客户后，你可以在之后的任意时间创建订阅。还可以传入可选的 `$options` 数组，提供额外的 [Paddle API 支持的客户创建参数](https://developer.paddle.com/api-reference/customers/create-customer)：

```php
$customer = $user->createAsCustomer($options);
```

<a name="subscriptions"></a>
## 订阅

<a name="creating-subscriptions"></a>
### 创建订阅

要创建订阅，首先从数据库中获取可计费模型的实例，通常是 `App\Models\User` 的实例。获取模型后，可以使用 `subscribe` 方法为其创建结账会话：

```php
use Illuminate\Http\Request;

Route::get('/user/subscribe', function (Request $request) {
    $checkout = $request->user()->subscribe($premium = 'pri_123', 'default')
        ->returnTo(route('home'));

    return view('billing', ['checkout' => $checkout]);
});
```

`subscribe` 方法的第一个参数是用户订阅的具体价格，应与 Paddle 中的价格标识符对应。`returnTo` 方法接收一个 URL，用户成功完成结账后会被重定向到该地址。`subscribe` 方法的第二个参数是订阅的内部「类型」。如果应用只提供一种订阅，可以将其命名为 `default` 或 `primary`。该类型仅供应用内部使用，不应显示给用户；它不能包含空格，且在创建订阅后绝不能更改。

你也可以使用 `customData` 方法提供包含订阅自定义元数据的数组：

```php
$checkout = $request->user()->subscribe($premium = 'pri_123', 'default')
    ->customData(['key' => 'value'])
    ->returnTo(route('home'));
```

创建订阅结账会话后，可以将其传给 Cashier Paddle 提供的 `paddle-button` [Blade 组件](#overlay-checkout)：

```blade
<x-paddle-button :checkout="$checkout" class="px-8 py-4">
    Subscribe
</x-paddle-button>
```

用户完成结账后，Paddle 会发送 `subscription_created` Webhook。Cashier 收到该 Webhook 后会为客户设置订阅。为确保应用正确接收并处理所有 Webhook，请确保已正确[配置 Webhook 处理](#handling-paddle-webhooks)。

<a name="checking-subscription-status"></a>
### 检查订阅状态

用户订阅应用后，你可以使用多种便捷方法检查订阅状态。首先，如果用户拥有有效订阅，`subscribed` 方法会返回 `true`，即使订阅仍处于试用期也是如此：

```php
if ($user->subscribed()) {
    // ...
}
```

如果应用提供多个订阅，可以在调用 `subscribed` 方法时指定订阅：

```php
if ($user->subscribed('default')) {
    // ...
}
```

`subscribed` 方法也适合用于[路由中间件](/docs/{{version}}/middleware)，以便根据用户的订阅状态限制对路由和控制器的访问：

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
        if ($request->user() && ! $request->user()->subscribed()) {
            // 该用户不是付费客户……
            return redirect('/billing');
        }

        return $next($request);
    }
}
```

要判断用户是否仍处于试用期，可以使用 `onTrial` 方法。该方法有助于判断是否应向用户显示试用期提示：

```php
if ($user->subscription()->onTrial()) {
    // ...
}
```

`subscribedToPrice` 方法可根据 Paddle 价格 ID 判断用户是否订阅了指定方案。在此示例中，我们判断用户的 `default` 订阅是否有效地订阅了月付价格：

```php
if ($user->subscribedToPrice($monthly = 'pri_123', 'default')) {
    // ...
}
```

`recurring` 方法可用于判断用户当前是否拥有有效订阅，并且不再处于试用期或宽限期：

```php
if ($user->subscription()->recurring()) {
    // ...
}
```

<a name="canceled-subscription-status"></a>
#### 已取消订阅的状态

要判断用户是否曾有有效订阅但已取消，可以使用 `canceled` 方法：

```php
if ($user->subscription()->canceled()) {
    // ...
}
```

你也可以判断用户是否已取消订阅，但在订阅完全到期前仍处于「宽限期」。例如，用户在 3 月 5 日取消了原定于 3 月 10 日到期的订阅，那么宽限期会持续到 3 月 10 日。在此期间，`subscribed` 方法仍会返回 `true`：

```php
if ($user->subscription()->onGracePeriod()) {
    // ...
}
```

<a name="past-due-status"></a>
#### 逾期状态

如果订阅支付失败，订阅会被标记为 `past_due`。处于此状态时，订阅在客户更新支付信息之前不会生效。你可以使用订阅实例的 `pastDue` 方法判断订阅是否逾期：

```php
if ($user->subscription()->pastDue()) {
    // ...
}
```

订阅逾期时，应引导用户[更新支付信息](#updating-payment-information)。

如果希望订阅在 `past_due` 状态下仍被视为有效，可以使用 Cashier 提供的 `keepPastDueSubscriptionsActive` 方法。通常应在 `AppServiceProvider` 的 `register` 方法中调用：

```php
use Laravel\Paddle\Cashier;

/**
 * 注册应用服务。
 */
public function register(): void
{
    Cashier::keepPastDueSubscriptionsActive();
}
```

> [!WARNING]
> 订阅处于 `past_due` 状态时，在支付信息更新之前无法更改。因此，此时调用 `swap` 和 `updateQuantity` 方法会抛出异常。

<a name="subscription-scopes"></a>
#### 订阅查询作用域

大多数订阅状态也可作为查询作用域使用，方便你查询数据库中处于特定状态的订阅：

```php
// 获取所有有效订阅……
$subscriptions = Subscription::query()->valid()->get();

// 获取用户的所有已取消订阅……
$subscriptions = $user->subscriptions()->canceled()->get();
```

可用的查询作用域完整列表如下：

```php
Subscription::query()->valid();
Subscription::query()->onTrial();
Subscription::query()->expiredTrial();
Subscription::query()->notOnTrial();
Subscription::query()->active();
Subscription::query()->recurring();
Subscription::query()->pastDue();
Subscription::query()->paused();
Subscription::query()->notPaused();
Subscription::query()->onPausedGracePeriod();
Subscription::query()->notOnPausedGracePeriod();
Subscription::query()->canceled();
Subscription::query()->notCanceled();
Subscription::query()->onGracePeriod();
Subscription::query()->notOnGracePeriod();
```

<a name="subscription-single-charges"></a>
### 订阅单次收费

订阅单次收费允许你在订阅费用之外向订阅者收取一次性费用。调用 `charge` 方法时，必须提供一个或多个价格 ID：

```php
// 收取一个价格……
$response = $user->subscription()->charge('pri_123');

// 一次收取多个价格……
$response = $user->subscription()->charge(['pri_123', 'pri_456']);
```

`charge` 方法要到订阅的下一个计费周期才会实际向客户收费。如果希望立即收费，可以改用 `chargeAndInvoice` 方法：

```php
$response = $user->subscription()->chargeAndInvoice('pri_123');
```

<a name="updating-payment-information"></a>
### 更新支付信息

Paddle 会为每个订阅保存一个支付方式。要更新订阅的默认支付方式，应使用订阅模型的 `redirectToUpdatePaymentMethod` 方法，将客户重定向到 Paddle 托管的支付方式更新页面：

```php
use Illuminate\Http\Request;

Route::get('/update-payment-method', function (Request $request) {
    $user = $request->user();

    return $user->subscription()->redirectToUpdatePaymentMethod();
});
```

用户完成信息更新后，Paddle 会发送 `subscription_updated` Webhook，应用数据库中的订阅信息也会随之更新。

<a name="changing-plans"></a>
### 更改方案

用户订阅应用后，可能会希望切换到新的订阅方案。要更新用户的订阅方案，应将 Paddle 价格标识符传给订阅的 `swap` 方法：

```php
use App\Models\User;

$user = User::find(1);

$user->subscription()->swap($premium = 'pri_456');
```

如果希望切换方案后立即向用户开具发票，而不是等待下一个计费周期，可以使用 `swapAndInvoice` 方法：

```php
$user = User::find(1);

$user->subscription()->swapAndInvoice($premium = 'pri_456');
```

<a name="prorations"></a>
#### 按比例分摊

默认情况下，Paddle 在切换方案时会按比例分摊费用。可以使用 `noProrate` 方法更新订阅，而不按比例分摊费用：

```php
$user->subscription('default')->noProrate()->swap($premium = 'pri_456');
```

如果希望禁用按比例分摊并立即向客户开具发票，可以结合使用 `swapAndInvoice` 和 `noProrate` 方法：

```php
$user->subscription('default')->noProrate()->swapAndInvoice($premium = 'pri_456');
```

或者，如果不希望因订阅变更向客户收费，可以使用 `doNotBill` 方法：

```php
$user->subscription('default')->doNotBill()->swap($premium = 'pri_456');
```

有关 Paddle 按比例分摊政策的更多信息，请参阅其[按比例分摊文档](https://developer.paddle.com/concepts/subscriptions/proration)。

<a name="subscription-quantity"></a>
### 订阅数量

有时订阅会受「数量」影响。例如，项目管理应用可能会按每个项目每月 10 美元收费。可以使用 `incrementQuantity` 和 `decrementQuantity` 方法轻松增加或减少订阅数量：

```php
$user = User::find(1);

$user->subscription()->incrementQuantity();

// 在订阅当前数量上增加五个……
$user->subscription()->incrementQuantity(5);

$user->subscription()->decrementQuantity();

// 在订阅当前数量上减少五个……
$user->subscription()->decrementQuantity(5);
```

你也可以使用 `updateQuantity` 方法设置指定数量：

```php
$user->subscription()->updateQuantity(10);
```

可以使用 `noProrate` 方法更新订阅数量，而不按比例分摊费用：

```php
$user->subscription()->noProrate()->updateQuantity(10);
```

<a name="quantities-for-subscription-with-multiple-products"></a>
#### 多产品订阅的数量

如果订阅包含[多个产品](#subscriptions-with-multiple-products)，应将需要增加或减少数量的价格 ID 作为第二个参数传给增减数量的方法：

```php
$user->subscription()->incrementQuantity(1, 'price_chat');
```

<a name="subscriptions-with-multiple-products"></a>
### 多产品订阅

[多产品订阅](https://developer.paddle.com/build/subscriptions/add-remove-products-prices-addons)允许你将多个计费产品分配给同一个订阅。例如，假设你正在构建一个客户服务「帮助台」应用，其基础订阅价格为每月 10 美元，同时提供一个每月额外收费 15 美元的实时聊天附加产品。

创建订阅结账会话时，可以将价格数组作为第一个参数传给 `subscribe` 方法，为订阅指定多个产品：

```php
use Illuminate\Http\Request;

Route::post('/user/subscribe', function (Request $request) {
    $checkout = $request->user()->subscribe([
        'price_monthly',
        'price_chat',
    ]);

    return view('billing', ['checkout' => $checkout]);
});
```

上例中，客户的 `default` 订阅将关联两个价格，分别按照各自的计费周期收费。必要时，可以传入键值对组成的关联数组，指定每个价格的数量：

```php
$user = User::find(1);

$checkout = $user->subscribe(['price_monthly', 'price_chat' => 5]);
```

要向现有订阅添加另一个价格，必须使用订阅的 `swap` 方法。调用时，还应包含订阅当前的价格和数量：

```php
$user = User::find(1);

$user->subscription()->swap(['price_chat', 'price_original' => 2]);
```

上例会添加新价格，但客户要到下一个计费周期才会为其付费。如果希望立即收费，可以使用 `swapAndInvoice` 方法：

```php
$user->subscription()->swapAndInvoice(['price_chat', 'price_original' => 2]);
```

你可以使用 `swap` 方法并省略要移除的价格，来从订阅中移除价格：

```php
$user->subscription()->swap(['price_original' => 2]);
```

> [!WARNING]
> 不能移除订阅中的最后一个价格；应直接取消订阅。

<a name="multiple-subscriptions"></a>
### 多个订阅

Paddle 允许客户同时拥有多个订阅。例如，一家健身房可能提供游泳和举重订阅，每种订阅的价格各不相同。客户可以订阅其中一种或两种方案。

应用创建订阅时，可以将订阅类型作为第二个参数传给 `subscribe` 方法。类型可以是表示用户所创建订阅类型的任意字符串：

```php
use Illuminate\Http\Request;

Route::post('/swimming/subscribe', function (Request $request) {
    $checkout = $request->user()->subscribe($swimmingMonthly = 'pri_123', 'swimming');

    return view('billing', ['checkout' => $checkout]);
});
```

在此示例中，我们为客户创建了月付游泳订阅。客户之后可能希望切换为年付订阅；调整时，只需切换 `swimming` 订阅的价格：

```php
$user->subscription('swimming')->swap($swimmingYearly = 'pri_456');
```

当然，你也可以直接取消该订阅：

```php
$user->subscription('swimming')->cancel();
```

<a name="pausing-subscriptions"></a>
### 暂停订阅

要暂停订阅，请在用户的订阅上调用 `pause` 方法：

```php
$user->subscription()->pause();
```

暂停订阅时，Cashier 会自动设置数据库中的 `paused_at` 列，用于判断 `paused` 方法何时应开始返回 `true`。例如，客户在 3 月 1 日暂停订阅，但订阅原定于 3 月 5 日续费，则 `paused` 方法会在 3 月 5 日之前继续返回 `false`。这是因为通常允许用户在计费周期结束前继续使用应用。

默认情况下，暂停会在下一个计费周期生效，让客户继续使用已付费周期的剩余时间。如果希望立即暂停订阅，可以使用 `pauseNow` 方法：

```php
$user->subscription()->pauseNow();
```

使用 `pauseUntil` 方法可以将订阅暂停至指定时间：

```php
$user->subscription()->pauseUntil(now()->plus(months: 1));
```

或者，可以使用 `pauseNowUntil` 方法立即暂停订阅，直至指定时间：

```php
$user->subscription()->pauseNowUntil(now()->plus(months: 1));
```

可以使用 `onPausedGracePeriod` 方法判断用户是否已暂停订阅但仍处于「宽限期」：

```php
if ($user->subscription()->onPausedGracePeriod()) {
    // ...
}
```

要恢复已暂停的订阅，可以在订阅上调用 `resume` 方法：

```php
$user->subscription()->resume();
```

> [!WARNING]
> 订阅暂停期间无法修改。如果要切换方案或更新数量，必须先恢复订阅。

<a name="canceling-subscriptions"></a>
### 取消订阅

要取消订阅，请在用户的订阅上调用 `cancel` 方法：

```php
$user->subscription()->cancel();
```

取消订阅时，Cashier 会自动设置数据库中的 `ends_at` 列，用于判断 `subscribed` 方法何时应开始返回 `false`。例如，客户在 3 月 1 日取消订阅，但订阅原定于 3 月 5 日结束，则 `subscribed` 方法在 3 月 5 日之前仍会返回 `true`。这是因为通常允许用户在计费周期结束前继续使用应用。

可以使用 `onGracePeriod` 方法判断用户是否已取消订阅但仍处于「宽限期」：

```php
if ($user->subscription()->onGracePeriod()) {
    // ...
}
```

如果希望立即取消订阅，可以在订阅上调用 `cancelNow` 方法：

```php
$user->subscription()->cancelNow();
```

要阻止处于宽限期的订阅被取消，可以调用 `stopCancelation` 方法：

```php
$user->subscription()->stopCancelation();
```

> [!WARNING]
> Paddle 订阅取消后无法恢复。如果客户希望继续订阅，必须创建新的订阅。

<a name="subscription-trials"></a>
## 订阅试用

<a name="with-payment-method-up-front"></a>
### 预先提供支付方式

如果希望为客户提供试用期，同时预先收集支付方式信息，应在 Paddle 控制面板中为客户订阅的价格设置试用时长，然后照常创建结账会话：

```php
use Illuminate\Http\Request;

Route::get('/user/subscribe', function (Request $request) {
    $checkout = $request->user()
        ->subscribe('pri_monthly')
        ->returnTo(route('home'));

    return view('billing', ['checkout' => $checkout]);
});
```

应用收到 `subscription_created` 事件时，Cashier 会在数据库的订阅记录中设置试用结束日期，并指示 Paddle 在该日期之后才开始向客户收费。

> [!WARNING]
> 如果客户的订阅在试用结束日期之前未被取消，试用到期后将立即收费，因此务必通知用户试用结束日期。

可以使用用户实例的 `onTrial` 方法判断用户是否处于试用期：

```php
if ($user->onTrial()) {
    // ...
}
```

要判断现有试用期是否已过期，可以使用 `hasExpiredTrial` 方法：

```php
if ($user->hasExpiredTrial()) {
    // ...
}
```

要判断用户是否处于特定订阅类型的试用期，可以将类型传给 `onTrial` 或 `hasExpiredTrial` 方法：

```php
if ($user->onTrial('default')) {
    // ...
}

if ($user->hasExpiredTrial('default')) {
    // ...
}
```

<a name="without-payment-method-up-front"></a>
### 不预先提供支付方式

如果希望提供试用期而不预先收集用户的支付方式信息，可以将用户关联的客户记录上的 `trial_ends_at` 列设置为期望的试用结束日期。通常在用户注册时完成：

```php
use App\Models\User;

$user = User::create([
    // ...
]);

$user->createAsCustomer([
    'trial_ends_at' => now()->plus(days: 10)
]);
```

Cashier 将这种试用称为「通用试用」，因为它不与任何现有订阅关联。如果当前日期尚未超过 `trial_ends_at` 的值，`User` 实例的 `onTrial` 方法会返回 `true`：

```php
if ($user->onTrial()) {
    // 用户处于试用期内……
}
```

准备好为用户创建实际订阅后，可以像往常一样使用 `subscribe` 方法：

```php
use Illuminate\Http\Request;

Route::get('/user/subscribe', function (Request $request) {
    $checkout = $request->user()
        ->subscribe('pri_monthly')
        ->returnTo(route('home'));

    return view('billing', ['checkout' => $checkout]);
});
```

要获取用户的试用结束日期，可以使用 `trialEndsAt` 方法。用户处于试用期时，该方法返回 Carbon 日期实例，否则返回 `null`。如果要获取默认订阅以外的特定订阅的试用结束日期，也可以传入可选的订阅类型参数：

```php
if ($user->onTrial('default')) {
    $trialEndsAt = $user->trialEndsAt();
}
```

如果希望明确判断用户是否处于「通用」试用期且尚未创建实际订阅，可以使用 `onGenericTrial` 方法：

```php
if ($user->onGenericTrial()) {
    // 用户处于「通用」试用期内……
}
```

<a name="extend-or-activate-a-trial"></a>
### 延长或激活试用

可以调用订阅的 `extendTrial` 方法并指定试用结束时间，以延长现有试用期：

```php
$user->subscription()->extendTrial(now()->plus(days: 5));
```

也可以在订阅上调用 `activate` 方法结束试用期，立即激活订阅：

```php
$user->subscription()->activate();
```

<a name="handling-paddle-webhooks"></a>
## 处理 Paddle Webhook

Paddle 可以通过 Webhook 向应用通知各种事件。默认情况下，Cashier 服务提供者会注册一个指向其 Webhook 控制器的路由，由该控制器处理所有传入的 Webhook 请求。

默认情况下，该控制器会自动处理因收费失败次数过多而取消订阅、订阅更新和支付方式变更。不过，你也可以扩展控制器来处理所需的任何 Paddle Webhook 事件。

为确保应用能够处理 Paddle Webhook，请务必[在 Paddle 控制面板中配置 Webhook URL](https://vendors.paddle.com/notifications-v2)。默认情况下，Cashier 的 Webhook 控制器响应 `/paddle/webhook` 路径。应在 Paddle 控制面板中启用的 Webhook 完整列表如下：

- Customer Updated（客户更新）
- Transaction Completed（交易完成）
- Transaction Updated（交易更新）
- Subscription Created（订阅创建）
- Subscription Updated（订阅更新）
- Subscription Paused（订阅暂停）
- Subscription Canceled（订阅取消）

> [!WARNING]
> 请务必使用 Cashier 自带的 [Webhook 签名验证](/docs/{{version}}/cashier-paddle#verifying-webhook-signatures)中间件保护传入请求。

<a name="webhooks-csrf-protection"></a>
#### Webhook 与 CSRF 保护

由于 Paddle Webhook 需要绕过 Laravel 的 [CSRF 保护](/docs/{{version}}/csrf)，应确保 Laravel 不会尝试验证传入的 Paddle Webhook 的 CSRF 令牌。为此，应在应用的 `bootstrap/app.php` 文件中将 `paddle/*` 排除在 CSRF 保护之外：

```php
->withMiddleware(function (Middleware $middleware): void {
    $middleware->preventRequestForgery(except: [
        'paddle/*',
    ]);
})
```

<a name="webhooks-local-development"></a>
#### Webhook 与本地开发

为了让 Paddle 在本地开发期间向应用发送 Webhook，需要通过 [Ngrok](https://ngrok.com/) 或 [Expose](https://expose.dev/docs/introduction) 等站点共享服务暴露应用。如果使用 [Laravel Sail](/docs/{{version}}/sail) 进行本地开发，可以使用 Sail 的[站点共享命令](/docs/{{version}}/sail#sharing-your-site)。

<a name="defining-webhook-event-handlers"></a>
### 定义 Webhook 事件处理器

Cashier 会自动处理因收费失败而取消订阅及其他常见的 Paddle Webhook。如果还需要处理其他 Webhook 事件，可以监听 Cashier 分发的以下事件：

- `Laravel\Paddle\Events\WebhookReceived`
- `Laravel\Paddle\Events\WebhookHandled`

这两个事件都包含 Paddle Webhook 的完整载荷。例如，要处理 `transaction.billed` Webhook，可以注册一个[监听器](/docs/{{version}}/events#defining-listeners)：

```php
<?php

namespace App\Listeners;

use Laravel\Paddle\Events\WebhookReceived;

class PaddleEventListener
{
    /**
     * 处理收到的 Paddle Webhook。
     */
    public function handle(WebhookReceived $event): void
    {
        if ($event->payload['event_type'] === 'transaction.billed') {
            // 处理传入的事件……
        }
    }
}
```

Cashier 还会根据收到的 Webhook 类型分发专门的事件。除了 Paddle 的完整载荷，这些事件还包含处理 Webhook 所用的相关模型，例如可计费模型、订阅或收据：

<div class="content-list" markdown="1">

- `Laravel\Paddle\Events\CustomerUpdated`
- `Laravel\Paddle\Events\TransactionCompleted`
- `Laravel\Paddle\Events\TransactionUpdated`
- `Laravel\Paddle\Events\SubscriptionCreated`
- `Laravel\Paddle\Events\SubscriptionUpdated`
- `Laravel\Paddle\Events\SubscriptionPaused`
- `Laravel\Paddle\Events\SubscriptionCanceled`

</div>

你也可以在应用的 `.env` 文件中定义 `CASHIER_WEBHOOK` 环境变量，覆盖默认的内置 Webhook 路由。该值应为 Webhook 路由的完整 URL，并须与 Paddle 控制面板中设置的 URL 一致：

```ini
CASHIER_WEBHOOK=https://example.com/my-paddle-webhook-url
```

<a name="verifying-webhook-signatures"></a>
### 验证 Webhook 签名

为保护 Webhook，可以使用 [Paddle 的 Webhook 签名](https://developer.paddle.com/webhooks/signature-verification)。为方便起见，Cashier 自动提供了一个中间件，用于验证传入的 Paddle Webhook 请求。

要启用 Webhook 验证，请确保应用的 `.env` 文件中定义了 `PADDLE_WEBHOOK_SECRET` 环境变量。Webhook 密钥可以从 Paddle 账户控制面板获取。

<a name="single-charges"></a>
## 单次收费

<a name="charging-for-products"></a>
### 产品收费

要为客户发起产品购买，可以使用可计费模型实例的 `checkout` 方法生成结账会话。该方法接收一个或多个价格 ID；必要时，可以使用关联数组提供购买产品的数量：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $request->user()->checkout(['pri_tshirt', 'pri_socks' => 5]);

    return view('buy', ['checkout' => $checkout]);
});
```

生成结账会话后，可以使用 Cashier 提供的 `paddle-button` [Blade 组件](#overlay-checkout)，让用户查看 Paddle 结账组件并完成购买：

```blade
<x-paddle-button :checkout="$checkout" class="px-8 py-4">
    Buy
</x-paddle-button>
```

结账会话提供 `customData` 方法，让你向底层交易创建过程传入自定义数据。有关传入自定义数据时可用选项的更多信息，请参阅 [Paddle 文档](https://developer.paddle.com/build/transactions/custom-data)：

```php
$checkout = $user->checkout('pri_tshirt')
    ->customData([
        'custom_option' => $value,
    ]);
```

<a name="refunding-transactions"></a>
### 交易退款

交易退款会将退款金额退回客户购买时使用的支付方式。要为 Paddle 购买退款，可以使用 `Cashier\Paddle\Transaction` 模型的 `refund` 方法。第一个参数是退款原因，之后可传入包含一个或多个待退款价格 ID 及可选金额的关联数组。你可以使用 `transactions` 方法获取可计费模型的交易记录。

例如，假设要退还某笔交易中的 `pri_123` 和 `pri_456`：前者全额退款，后者只退还两美元：

```php
use App\Models\User;

$user = User::find(1);

$transaction = $user->transactions()->first();

$response = $transaction->refund('Accidental charge', [
    'pri_123', // 全额退还此价格……
    'pri_456' => 200, // 仅部分退还此价格……
]);
```

上例退还交易中的特定项目。如果要退还整笔交易，只需提供退款原因：

```php
$response = $transaction->refund('Accidental charge');
```

有关退款的更多信息，请参阅 [Paddle 退款文档](https://developer.paddle.com/build/transactions/create-transaction-adjustments)。

> [!WARNING]
> 退款在处理完成前必须经过 Paddle 批准。

<a name="crediting-transactions"></a>
### 交易贷记

与退款类似，你也可以为交易贷记。交易贷记会将资金加入客户余额，供其日后购买使用。贷记仅适用于手动收款的交易，不适用于自动收款的交易（如订阅），因为 Paddle 会自动处理订阅贷记：

```php
$transaction = $user->transactions()->first();

// 全额贷记指定的交易项目……
$response = $transaction->credit('Compensation', 'pri_123');
```

更多信息请参阅 [Paddle 的贷记文档](https://developer.paddle.com/build/transactions/create-transaction-adjustments)。

> [!WARNING]
> 贷记仅适用于手动收款的交易；自动收款的交易由 Paddle 自行处理贷记。

<a name="transactions"></a>
## 交易

你可以通过 `transactions` 属性轻松获取可计费模型的交易数组：

```php
use App\Models\User;

$user = User::find(1);

$transactions = $user->transactions;
```

交易表示产品及购买行为的付款记录，并附有发票。只有已完成的交易才会存储在应用数据库中。

为客户列出交易时，可以使用交易实例的方法显示相关支付信息。例如，你可以在表格中列出每笔交易，让用户轻松下载发票：

```html
<table>
    @foreach ($transactions as $transaction)
        <tr>
            <td>{{ $transaction->billed_at->toFormattedDateString() }}</td>
            <td>{{ $transaction->total() }}</td>
            <td>{{ $transaction->tax() }}</td>
            <td><a href="{{ route('download-invoice', $transaction->id) }}" target="_blank">Download</a></td>
        </tr>
    @endforeach
</table>
```

`download-invoice` 路由可以如下定义：

```php
use Illuminate\Http\Request;
use Laravel\Paddle\Transaction;

Route::get('/download-invoice/{transaction}', function (Request $request, Transaction $transaction) {
    return $transaction->redirectToInvoicePdf();
})->name('download-invoice');
```

<a name="past-and-upcoming-payments"></a>
### 过往与即将进行的付款

可以使用 `lastPayment` 和 `nextPayment` 方法获取并显示客户循环订阅的过往或即将进行的付款：

```php
use App\Models\User;

$user = User::find(1);

$subscription = $user->subscription();

$lastPayment = $subscription->lastPayment();
$nextPayment = $subscription->nextPayment();
```

这两个方法都会返回 `Laravel\Paddle\Payment` 实例；但当交易尚未通过 Webhook 同步时，`lastPayment` 返回 `null`；当计费周期已结束（例如订阅已取消）时，`nextPayment` 返回 `null`：

```blade
Next payment: {{ $nextPayment->amount() }} due on {{ $nextPayment->date()->format('d/m/Y') }}
```

<a name="testing"></a>
## 测试

测试时，应手动测试计费流程，确保集成按预期工作。

对于自动化测试（包括 CI 环境中的测试），可以使用 [Laravel HTTP 客户端](/docs/{{version}}/http-client#testing)模拟对 Paddle 的 HTTP 调用。虽然这样不会测试 Paddle 的实际响应，但可以在不实际调用 Paddle API 的情况下测试应用。
