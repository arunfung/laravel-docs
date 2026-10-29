
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
- [快速开始](#quickstart)
    - [销售产品](#quickstart-selling-products)
    - [销售订阅](#quickstart-selling-subscriptions)
- [结账会话](#checkout-sessions)
    - [覆盖式结账](#overlay-checkout)
    - [嵌入式结账](#inline-checkout)
    - [访客结账](#guest-checkouts)
- [价格预览](#price-previews)
    - [客户价格预览](#customer-price-previews)
    - [折扣](#price-discounts)
- [客户](#customers)
    - [客户默认值](#customer-defaults)
    - [检索客户](#retrieving-customers)
    - [创建客户](#creating-customers)
- [订阅](#subscriptions)
    - [创建订阅](#creating-subscriptions)
    - [检查订阅状态](#checking-subscription-status)
    - [订阅单次收费](#subscription-single-charges)
    - [更新支付信息](#updating-payment-information)
    - [更改计划](#changing-plans)
    - [订阅数量](#subscription-quantity)
    - [包含多个产品的订阅](#subscriptions-with-multiple-products)
    - [多个订阅](#multiple-subscriptions)
    - [暂停订阅](#pausing-subscriptions)
    - [取消订阅](#canceling-subscriptions)
- [订阅试用](#subscription-trials)
    - [预先提供支付方式](#with-payment-method-up-front)
    - [无需预先提供支付方式](#without-payment-method-up-front)
    - [延长或激活试用](#extend-or-activate-a-trial)
- [处理 Paddle Webhook](#handling-paddle-webhooks)
    - [定义 Webhook 事件处理器](#defining-webhook-event-handlers)
    - [验证 Webhook 签名](#verifying-webhook-signatures)
- [单次收费](#single-charges)
    - [产品收费](#charging-for-products)
    - [退款交易](#refunding-transactions)
    - [信用交易](#crediting-transactions)
- [交易](#transactions)
    - [过去和即将到来的付款](#past-and-upcoming-payments)
- [测试](#testing)

<a name="introduction"></a>
## 简介

> [!WARNING]
> 本文档适用于 Cashier Paddle 2.x 与 Paddle Billing 的集成。如果您仍在使用 Paddle Classic，您应该使用 [Cashier Paddle 1.x](https://github.com/laravel/cashier-paddle/tree/1.x)。

[Laravel Cashier Paddle](https://github.com/laravel/cashier-paddle) 为 [Paddle](https://paddle.com) 的订阅计费服务提供了一个富有表现力、流畅的接口。它处理了几乎所有您不愿编写的订阅计费样板代码。除了基本的订阅管理外，Cashier 还可以处理：交换订阅、订阅"数量"、订阅暂停、取消宽限期等。

在深入了解 Cashier Paddle 之前，我们建议你也先查看 Paddle 的 [概念指南](https://developer.paddle.com/concepts/overview) 以及 [API 文档](https://developer.paddle.com/api-reference/overview)。

## 升级 Cashier

当升级到 Cashier 的新版本时，务必要仔细阅读 [升级指南](https://github.com/laravel/cashier-paddle/blob/master/UPGRADE.md)。

## 安装

首先，使用 Composer 包管理器安装适用于 Paddle 的 Cashier 包：

```shell
composer require laravel/cashier-paddle
```

接下来，你需要使用 `vendor:publish` Artisan 命令发布 Cashier 的迁移文件：

```shell
php artisan vendor:publish --tag="cashier-migrations"
```

然后，你需要运行应用的数据库迁移。Cashier 的迁移将会创建一个新的 `customers` 表。此外，还会创建 `subscriptions` 和 `subscription_items` 表，用于存储所有客户的订阅信息。最后，还会创建一个 `transactions` 表，用于存储与你的客户相关联的所有 Paddle 交易记录：

```shell
php artisan migrate
```

> [!警告]
> 为确保 Cashier 能正确处理所有 Paddle 事件，请务必记得 [设置 Cashier 的 webhook 处理](#handling-paddle-webhooks)。

### Paddle 沙盒（Sandbox）

在本地及预发布（staging）开发阶段，你应该先 [注册 Paddle Sandbox 账号](https://sandbox-login.paddle.com/signup)。该账号将为你提供一个沙盒环境，让你在不产生真实支付的情况下测试和开发应用。你可以使用 Paddle 的 [测试银行卡号](https://developer.paddle.com/concepts/payment-methods/credit-debit-card) 来模拟不同的支付场景。

当使用 Paddle Sandbox 环境时，你需要在应用的 `.env` 文件中将 `PADDLE_SANDBOX` 环境变量设置为 `true`：

```ini
PADDLE_SANDBOX=true
```



在你完成应用开发之后，你可以 [申请 Paddle 供应商（vendor）账号](https://paddle.com)。在你的应用正式上线生产环境之前，Paddle 需要先审核并批准你应用所使用的域名。

## 配置（Configuration）

### 可计费模型（Billable Model）

在使用 Cashier 之前，你必须先在用户模型（User Model）定义中添加 `Billable` trait。该 trait 提供了多种方法，让你可以执行常见的计费操作，例如创建订阅（subscription）以及更新支付方式信息：

```php
use Laravel\Paddle\Billable;

class User extends Authenticatable
{
    use Billable;
}
```

如果你有需要计费的实体不是用户（User），你也可以在这些类中添加该 trait：

```php
use Illuminate\Database\Eloquent\Model;
use Laravel\Paddle\Billable;

class Team extends Model
{
    use Billable;
}
```

### API 密钥（API Keys）

接下来，你需要在应用的 `.env` 文件中配置 Paddle 的密钥。你可以在 Paddle 控制面板（control panel）中获取 Paddle 的 API 密钥：

```ini
PADDLE_CLIENT_SIDE_TOKEN=your-paddle-client-side-token
PADDLE_API_KEY=your-paddle-api-key
PADDLE_RETAIN_KEY=your-paddle-retain-key
PADDLE_WEBHOOK_SECRET="your-paddle-webhook-secret"
PADDLE_SANDBOX=true
```

当你使用 [Paddle 的 Sandbox（沙盒）环境](#paddle-sandbox) 时，`PADDLE_SANDBOX` 环境变量应设置为 `true`。如果你要将应用部署到生产环境，并使用 Paddle 的正式（live）供应商环境，则应将 `PADDLE_SANDBOX` 设置为 `false`。

`PADDLE_RETAIN_KEY` 是可选项，仅在你使用 Paddle 的 [Retain 功能](https://developer.paddle.com/paddlejs/retain) 时才需要设置。

### Paddle JS

Paddle 依赖它自己的 JavaScript 库来启动 Paddle 结算（checkout）小部件（widget）。你可以通过将 `@paddleJS` Blade 指令放在应用布局（layout）文件 `</head>` 结束标签之前来加载该 JavaScript 库：

```blade
<head>
    ...

    @paddleJS
</head>
```



### 货币配置（Currency Configuration）

你可以指定在发票上显示金额时使用的地区（locale）。在内部，Cashier 使用 [PHP 的 `NumberFormatter` 类](https://www.php.net/manual/en/class.numberformatter.php) 来设置货币地区：

```ini
CASHIER_CURRENCY_LOCALE=nl_BE
```

> [!警告]
> 为了使用除 `en` 之外的地区，请确保服务器已安装并配置 `ext-intl` PHP 扩展。

### 覆盖默认模型（Overriding Default Models）

你可以自由扩展 Cashier 内部使用的模型，通过定义你自己的模型并继承相应的 Cashier 模型：

```php
use Laravel\Paddle\Subscription as CashierSubscription;

class Subscription extends CashierSubscription
{
    // ...
}
```

在定义模型之后，你可以通过 `Laravel\Paddle\Cashier` 类告诉 Cashier 使用你的自定义模型。通常，你应该在应用的 `App\Providers\AppServiceProvider` 类的 `boot` 方法中通知 Cashier 你的自定义模型：

```php
use App\Models\Cashier\Subscription;
use App\Models\Cashier\Transaction;

/**
 * 引导（初始化）任何应用服务。
 */
public function boot(): void
{
    Cashier::useSubscriptionModel(Subscription::class);
    Cashier::useTransactionModel(Transaction::class);
}
```

## 快速开始（Quickstart）

### 销售产品（Selling Products）

> [!注意]
> 在使用 Paddle Checkout 之前，你应在 Paddle 控制面板中定义固定价格的产品。此外，你还应 [配置 Paddle 的 webhook 处理](#handling-paddle-webhooks)。

通过你的应用提供产品和订阅计费可能会让人觉得复杂。不过，多亏了 Cashier 和 [Paddle 的 Checkout Overlay](https://www.paddle.com/billing/checkout)，你可以轻松构建现代且可靠的支付集成。

要对非重复、一次性收费的产品向客户收费，我们将使用 Cashier 结合 Paddle 的 Checkout Overlay，让客户提供支付信息并确认购买。一旦通过 Checkout Overlay 完成支付，客户将被重定向到你应用中指定的成功页面 URL：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $request->user()->checkout('pri_deluxe_album')
        ->returnTo(route('dashboard'));

    return view('buy', ['checkout' => $checkout]);
})->name('checkout');
```



如上例所示，我们将使用 Cashier 提供的 `checkout` 方法来创建一个 checkout 对象，以向客户展示给定“价格标识符（price identifier）”的 Paddle Checkout Overlay。在使用 Paddle 时，“价格”是指 [为特定产品定义的价格](https://developer.paddle.com/build/products/create-products-prices)。

如有必要，`checkout` 方法会自动在 Paddle 中创建一个客户，并将该 Paddle 客户记录与应用数据库中的对应用户关联。在完成结账（checkout）会话后，客户将被重定向到一个专门的成功页面，在该页面你可以向客户显示相关信息。

在 `buy` 视图中，我们将包含一个按钮，用于显示 Checkout Overlay。`paddle-button` Blade 组件随 Cashier Paddle 一起提供；不过，你也可以 [手动渲染 Overlay Checkout](#manually-rendering-an-overlay-checkout)：

```html
<x-paddle-button :checkout="$checkout" class="px-8 py-4">
    Buy Product
</x-paddle-button>
```

#### 向 Paddle Checkout 提供元数据（Providing Meta Data to Paddle Checkout）

在销售产品时，通常会通过应用自定义的 `Cart` 和 `Order` 模型来跟踪已完成的订单和购买的产品。当将客户重定向到 Paddle 的 Checkout Overlay 完成购买时，你可能需要提供一个已有的订单标识符，以便在客户被重定向回你的应用时，将已完成的购买与对应订单关联起来。

为实现此功能，你可以向 `checkout` 方法提供一个自定义数据数组。假设在用户开始结账流程时，我们的应用会创建一个待处理（pending）的 `Order`。请记住，本示例中的 `Cart` 和 `Order` 模型仅用于说明，并非 Cashier 提供。你可以根据自己应用的需求自由实现这些概念：

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



如上例所示，当用户开始结账流程时，我们会将购物车/订单关联的所有 Paddle 价格标识符（price identifiers）提供给 `checkout` 方法。当然，你的应用需要负责在客户添加商品时，将这些项目与“购物车”或订单关联。我们还通过 `customData` 方法将订单的 ID 提供给 Paddle Checkout Overlay。

当然，一旦客户完成结账流程，你可能希望将订单标记为“已完成”。为实现此功能，你可以监听 Paddle 分发的 webhook，并通过 Cashier 触发的事件，将订单信息存储到你的数据库中。

首先，监听 Cashier 分发的 `TransactionCompleted` 事件。通常，你应在应用的 `App\Providers\AppServiceProvider` 的 `boot` 方法中注册事件监听器：

```php
use App\Listeners\CompleteOrder;
use Illuminate\Support\Facades\Event;
use Laravel\Paddle\Events\TransactionCompleted;

/**
 * 引导（初始化）任何应用服务。
 */
public function boot(): void
{
    Event::listen(TransactionCompleted::class, CompleteOrder::class);
}
```

在本示例中，`CompleteOrder` 监听器可能如下所示：

```php
namespace App\Listeners;

use App\Models\Order;
use Laravel\Paddle\Cashier;
use Laravel\Paddle\Events\TransactionCompleted;

class CompleteOrder
{
    /**
     * 处理传入的 Cashier webhook 事件。
     */
    public function handle(TransactionCompleted $event): void
    {
        $orderId = $event->payload['data']['custom_data']['order_id'] ?? null;

        $order = Order::findOrFail($orderId);

        $order->update(['status' => 'completed']);
    }
}
```

有关 `transaction.completed` 事件包含的数据的更多信息，请参阅 Paddle 的文档：[transaction.completed 事件数据](https://developer.paddle.com/webhooks/transactions/transaction-completed)。



### 销售订阅（Selling Subscriptions）

> [!注意]
> 在使用 Paddle Checkout 之前，你应在 Paddle 控制面板中定义固定价格的产品。此外，你还应 [配置 Paddle 的 webhook 处理](#handling-paddle-webhooks)。

通过你的应用提供产品和订阅计费可能会让人觉得复杂。不过，多亏了 Cashier 和 [Paddle 的 Checkout Overlay](https://www.paddle.com/billing/checkout)，你可以轻松构建现代且可靠的支付集成。

要学习如何使用 Cashier 和 Paddle 的 Checkout Overlay 销售订阅，我们可以考虑一个简单的场景：一个订阅服务提供基础月度（`price_basic_monthly`）和年度（`price_basic_yearly`）套餐。这两个价格可以在我们的 Paddle 控制面板中归类到“Basic”产品（`pro_basic`）下。此外，我们的订阅服务可能还提供一个专家计划（Expert plan）作为 `pro_expert`。

首先，让我们了解客户如何订阅我们的服务。当然，你可以想象客户可能会在应用的定价页面点击“订阅”按钮以选择 Basic 套餐。该按钮将调用 Paddle Checkout Overlay 来完成所选计划的支付。要开始操作，让我们通过 `checkout` 方法初始化一个结账会话：

```php
use Illuminate\Http\Request;

Route::get('/subscribe', function (Request $request) {
    $checkout = $request->user()->checkout('price_basic_monthly')
        ->returnTo(route('dashboard'));

    return view('subscribe', ['checkout' => $checkout]);
})->name('subscribe');
```

在 `subscribe` 视图中，我们将包含一个按钮，用于显示 Checkout Overlay。`paddle-button` Blade 组件随 Cashier Paddle 一起提供；不过，你也可以 [手动渲染 Overlay Checkout](#manually-rendering-an-overlay-checkout)：

```html
<x-paddle-button :checkout="$checkout" class="px-8 py-4">
    Subscribe
</x-paddle-button>
```



现在，当点击“Subscribe”按钮时，客户将能够输入他们的支付信息并启动订阅。由于某些支付方式可能需要几秒钟来处理支付，你还应 [配置 Cashier 的 webhook 处理](#handling-paddle-webhooks) 以便知道订阅何时实际开始。

既然客户可以开始订阅，我们需要限制应用的某些部分，使只有已订阅的用户才能访问。当然，我们可以通过 Cashier 的 `Billable` trait 提供的 `subscribed` 方法随时确定用户当前的订阅状态：

```blade
@if ($user->subscribed())
    <p>You are subscribed.</p>
@endif
```

我们甚至可以轻松判断用户是否订阅了特定的产品或价格：

```blade
@if ($user->subscribedToProduct('pro_basic'))
    <p>You are subscribed to our Basic product.</p>
@endif

@if ($user->subscribedToPrice('price_basic_monthly'))
    <p>You are subscribed to our monthly Basic plan.</p>
@endif
```

#### 创建订阅中间件（Building a Subscribed Middleware）

为了方便，你可能希望创建一个 [中间件](/docs/laravel/12.x/middleware)，用于判断传入请求是否来自已订阅的用户。一旦定义了该中间件，你就可以轻松地将其分配给路由，以阻止未订阅的用户访问该路由：

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class Subscribed
{
    /**
     * 处理传入请求。
     */
    public function handle(Request $request, Closure $next): Response
    {
        if (! $request->user()?->subscribed()) {
            // 将用户重定向到计费页面，并要求他们订阅...
            return redirect('/subscribe');
        }

        return $next($request);
    }
}
```



一旦中间件定义完成，你可以将其分配给某个路由：

```php
use App\Http\Middleware\Subscribed;

Route::get('/dashboard', function () {
    // ...
})->middleware([Subscribed::class]);
```

#### 允许客户管理他们的计费计划（Allowing Customers to Manage Their Billing Plan）

当然，客户可能希望将他们的订阅计划更改为另一个产品或“等级”。在我们上面的示例中，我们希望允许客户将计划从月度订阅更改为年度订阅。为此，你需要实现类似一个按钮，指向以下路由：

```php
use Illuminate\Http\Request;

Route::put('/subscription/{price}/swap', function (Request $request, $price) {
    $user->subscription()->swap($price); // 对于本示例，"$price" 为 "price_basic_yearly"。

    return redirect()->route('dashboard');
})->name('subscription.swap');
```

除了更换计划之外，你还需要允许客户取消订阅。与更换计划类似，提供一个按钮，指向以下路由：

```php
use Illuminate\Http\Request;

Route::put('/subscription/cancel', function (Request $request, $price) {
    $user->subscription()->cancel();

    return redirect()->route('dashboard');
})->name('subscription.cancel');
```

现在，客户的订阅将在其计费周期结束时被取消。

> [!注意]
> 只要你已配置 Cashier 的 webhook 处理，Cashier 将自动通过检查来自 Paddle 的传入 webhook 来保持应用中 Cashier 相关数据库表的同步。例如，当你通过 Paddle 控制面板取消客户订阅时，Cashier 会收到对应的 webhook，并在应用的数据库中将该订阅标记为“已取消（canceled）”。



## 结账会话（Checkout Sessions）

大多数对客户计费的操作都是通过 Paddle 的 [Checkout Overlay 小部件](https://developer.paddle.com/build/checkout/build-overlay-checkout) 或使用 [内联结账（inline checkout）](https://developer.paddle.com/build/checkout/build-branded-inline-checkout) 的“结账”完成的。

在使用 Paddle 处理结账支付之前，你应在 Paddle 结账设置控制面板中定义应用的 [默认支付链接（default payment link）](https://developer.paddle.com/build/transactions/default-payment-link#set-default-link)。

### Overlay Checkout

在显示 Checkout Overlay 小部件之前，你必须使用 Cashier 生成一个结账会话。结账会话将告知结账小部件应执行的计费操作：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $user->checkout('pri_34567')
        ->returnTo(route('dashboard'));

    return view('billing', ['checkout' => $checkout]);
});
```

Cashier 提供了一个 `paddle-button` [Blade 组件](/docs/laravel/12.x/blade#components)。你可以将结账会话作为“prop”传递给该组件。然后，当点击该按钮时，将显示 Paddle 的结账小部件：

```html
<x-paddle-button :checkout="$checkout" class="px-8 py-4">
    Subscribe
</x-paddle-button>
```

默认情况下，这将使用 Paddle 的默认样式显示小部件。你可以通过向组件添加 [Paddle 支持的属性](https://developer.paddle.com/paddlejs/html-data-attributes) 来自定义小部件，例如 `data-theme='light'` 属性：

```html
<x-paddle-button :checkout="$checkout" class="px-8 py-4" data-theme="light">
    Subscribe
</x-paddle-button>
```

Paddle 结账小部件是异步的。一旦用户在小部件中创建订阅，Paddle 会向你的应用发送 webhook，以便你正确更新应用数据库中的订阅状态。因此，正确 [设置 webhook](#handling-paddle-webhooks) 以处理来自 Paddle 的状态变更非常重要。

> [!警告]
> 在订阅状态更改后，收到相应 webhook 的延迟通常很短，但你应在应用中考虑到这一点，因为用户完成结账后，其订阅状态可能不会立即可用。



#### 手动渲染 Overlay Checkout（Manually Rendering an Overlay Checkout）

你也可以在不使用 Laravel 内置 Blade 组件的情况下，手动渲染 Overlay Checkout。首先，生成结账会话 [如前面的示例所示](#overlay-checkout)：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $user->checkout('pri_34567')
        ->returnTo(route('dashboard'));

    return view('billing', ['checkout' => $checkout]);
});
```

接下来，你可以使用 Paddle.js 初始化结账。在本示例中，我们将创建一个链接，并为其分配 `paddle_button` 类。Paddle.js 会检测该类，并在点击链接时显示 Overlay Checkout：

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

### 内联结账（Inline Checkout）

如果你不想使用 Paddle 的“Overlay”样式结账小部件，Paddle 也提供了在应用中内联显示小部件的选项。虽然这种方式不允许你调整结账的 HTML 字段，但它允许你将小部件嵌入到应用中。

为了方便你开始使用内联结账，Cashier 提供了一个 `paddle-checkout` Blade 组件。首先，你应 [生成一个结账会话](#overlay-checkout)：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $user->checkout('pri_34567')
        ->returnTo(route('dashboard'));

    return view('billing', ['checkout' => $checkout]);
});
```



然后，你可以将结账会话传递给组件的 `checkout` 属性：

```blade
<x-paddle-checkout :checkout="$checkout" class="w-full" />
```

要调整内联结账组件的高度，你可以将 `height` 属性传递给 Blade 组件：

```blade
<x-paddle-checkout :checkout="$checkout" class="w-full" height="500" />
```

有关内联结账自定义选项的更多详细信息，请参阅 Paddle 的 [内联结账指南](https://developer.paddle.com/build/checkout/build-branded-inline-checkout) 以及 [可用结账设置](https://developer.paddle.com/build/checkout/set-up-checkout-default-settings)。

#### 手动渲染内联结账（Manually Rendering an Inline Checkout）

你也可以在不使用 Laravel 内置 Blade 组件的情况下，手动渲染内联结账。首先，生成结账会话 [如前面示例所示](#inline-checkout)：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $user->checkout('pri_34567')
        ->returnTo(route('dashboard'));

    return view('billing', ['checkout' => $checkout]);
});
```

接下来，你可以使用 Paddle.js 初始化结账。在本示例中，我们将使用 [Alpine.js](https://github.com/alpinejs/alpine) 来演示；当然，你可以根据自己的前端技术栈修改此示例：

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

### 游客结账（Guest Checkouts）

有时，你可能需要为不需要在你的应用中注册账户的用户创建结账会话。为此，你可以使用 `guest` 方法：

```php
use Illuminate\Http\Request;
use Laravel\Paddle\Checkout;

Route::get('/buy', function (Request $request) {
    $checkout = Checkout::guest(['pri_34567'])
        ->returnTo(route('home'));

    return view('billing', ['checkout' => $checkout]);
});
```



然后，你可以将结账会话提供给 [Paddle 按钮](#overlay-checkout) 或 [内联结账](#inline-checkout) Blade 组件。

## 价格预览（Price Previews）

Paddle 允许你根据货币自定义价格，本质上可以为不同国家配置不同的价格。Cashier Paddle 允许你使用 `previewPrices` 方法获取所有这些价格。该方法接受你希望检索的价格 ID：

```php
use Laravel\Paddle\Cashier;

$prices = Cashier::previewPrices(['pri_123', 'pri_456']);
```

货币将根据请求的 IP 地址确定；不过，你也可以选择提供特定国家来检索价格：

```php
use Laravel\Paddle\Cashier;

$prices = Cashier::previewPrices(['pri_123', 'pri_456'], ['address' => [
    'country_code' => 'BE',
    'postal_code' => '1234',
]]);
```

获取价格后，你可以以任意方式显示它们：

```blade
<ul>
    @foreach ($prices as $price)
        <li>{{ $price->product['name'] }} - {{ $price->total() }}</li>
    @endforeach
</ul>
```

你也可以将小计价格和税额分别显示：

```blade
<ul>
    @foreach ($prices as $price)
        <li>{{ $price->product['name'] }} - {{ $price->subtotal() }} (+ {{ $price->tax() }} tax)</li>
    @endforeach
</ul>
```

有关更多信息，请参阅 Paddle 的 API 文档：[价格预览（price previews）](https://developer.paddle.com/api-reference/pricing-preview/preview-prices)。

### 客户价格预览（Customer Price Previews）

如果用户已经是客户，并且你希望显示适用于该客户的价格，你可以通过直接从客户实例中检索价格来实现：

```php
use App\Models\User;

$prices = User::find(1)->previewPrices(['pri_123', 'pri_456']);
```



在内部，Cashier 将使用用户的客户 ID 来检索其对应货币的价格。例如，居住在美国的用户将看到 **美元 (USD)** 价格，而居住在比利时的用户将看到 **欧元 (EUR)** 价格。如果未找到匹配的货币，则将使用产品的 **默认货币**。你可以在 **Paddle 控制面板** 中自定义产品或订阅计划的所有价格。

### 折扣

你也可以选择显示折扣后的价格。在调用 `previewPrices` 方法时，你需要通过 `discount_id` 选项提供折扣 ID：

```php
use Laravel\Paddle\Cashier;

$prices = Cashier::previewPrices(['pri_123', 'pri_456'], [
    'discount_id' => 'dsc_123'
]);
```

然后，显示计算后的价格：

```blade
<ul>
    @foreach ($prices as $price)
        <li>{{ $price->product['name'] }} - {{ $price->total() }}</li>
    @endforeach
</ul>
```

## 客户

### 客户默认值（Customer Defaults）

Cashier 允许你在创建结账（checkout）会话时，为客户定义一些有用的默认值。设置这些默认值可以预填充客户的 **电子邮件地址** 和 **姓名**，以便客户可以直接进入结账小组件（checkout widget）的支付部分。你可以在你的计费模型（billable model）中重写以下方法来设置这些默认值：

```php
/**
 * 获取要关联到 Paddle 的客户姓名
 */
public function paddleName(): string|null
{
    return $this->name;
}

/**
 * 获取要关联到 Paddle 的客户电子邮件地址
 */
public function paddleEmail(): string|null
{
    return $this->email;
}
```

这些默认设置将用于收银（Cashier）中生成 **[checkout session](#checkout-sessions)** 的每一个操作。


### 检索客户（Retrieving Customers）

你可以使用 `Cashier::findBillable` 方法，通过 Paddle Customer ID 来检索客户。此方法将返回一个可计费（billable）模型实例：

```php
use Laravel\Paddle\Cashier;

$user = Cashier::findBillable($customerId);
```

### 创建客户（Creating Customers）

偶尔，你可能希望在不启动订阅的情况下创建一个 Paddle 客户。你可以使用 `createAsCustomer` 方法来完成：

```php
$customer = $user->createAsCustomer();
```

返回的是 `Laravel\Paddle\Customer` 的一个实例。一旦该客户在 Paddle 中被创建，你可以在之后的某个时间再启动订阅。你也可以提供一个可选的 `$options` 数组，用于传入任何额外的 [Paddle API 支持的客户创建参数](https://developer.paddle.com/api-reference/customers/create-customer)：

```php
$customer = $user->createAsCustomer($options);
```

## 订阅

### 创建订阅（Creating Subscriptions）

要创建订阅，首先从你的数据库中检索一个可计费模型实例，该模型通常是 `App\Models\User` 的一个实例（一般代表用户）。在检索到模型实例后，你可以使用 `subscribe` 方法来创建该模型的结账会话（checkout session）：

```php
use Illuminate\Http\Request;

Route::get('/user/subscribe', function (Request $request) {
    $checkout = $request->user()->subscribe($premium = 'pri_123', 'default')
        ->returnTo(route('home'));

    return view('billing', ['checkout' => $checkout]);
});
```

传入 `subscribe` 方法的第一个参数是用户要订阅的具体价格（price）。该值应与 Paddle 中对应价格的标识符（identifier）一致。`returnTo` 方法接受一个 URL，用户在成功完成结账后将被重定向到该地址。传入 `subscribe` 方法的第二个参数应为订阅的内部“类型”（type）。如果你的应用只提供一种订阅，你可以将其命名为 `default` 或 `primary`。该订阅类型仅用于应用内部使用，并**不是**用于展示给用户的。此外，它不应包含空格，并且在创建订阅后**绝不能**更改。



你也可以使用 `customData` 方法提供一个包含订阅相关自定义元数据（metadata）的数组：

```php
$checkout = $request->user()->subscribe($premium = 'pri_123', 'default')
    ->customData(['key' => 'value'])
    ->returnTo(route('home'));
```

一旦订阅结账会话（subscription checkout session）被创建，该结账会话可以被传入 Cashier Paddle 内置的 `paddle-button` **[Blade 组件](#overlay-checkout)**：

```blade
<x-paddle-button :checkout="$checkout" class="px-8 py-4">
    Subscribe
</x-paddle-button>
```

当用户完成结账后，Paddle 将会发送一个 `subscription_created` webhook。Cashier 会接收该 webhook，并为你的客户（customer）完成订阅设置。为了确保所有 webhook 都能被你的应用正确接收和处理，请确认你已正确 **[完成 webhook 处理的设置](#handling-paddle-webhooks)**。

### 检查订阅状态（Checking Subscription Status）

当用户订阅你的应用后，你可以使用多种便捷方法来检查他们的订阅状态。首先，`subscribed` 方法会在用户拥有有效订阅时返回 `true`，**即使**该订阅目前仍处于试用期（trial period）：

```php
if ($user->subscribed()) {
    // ...
}
```

如果你的应用提供多个订阅，你可以在调用 `subscribed` 方法时指定订阅类型：

```php
if ($user->subscribed('default')) {
    // ...
}
```

`subscribed` 方法也非常适合作为 **[路由中间件](/docs/laravel/12.x/middleware)** 的候选，可用于根据用户的订阅状态来过滤对路由和控制器的访问：

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureUserIsSubscribed
{
    /**
     * 处理传入请求。
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next): Response
    {
        if ($request->user() && ! $request->user()->subscribed()) {
            // 该用户不是付费客户（paying customer）...
            return redirect('/billing');
        }

        return $next($request);
    }
}
```



如果你想判断用户是否仍处于试用期（trial period），可以使用 `onTrial` 方法。该方法对于判断是否应该向用户显示“仍在试用期”的提示非常有用：

```php
if ($user->subscription()->onTrial()) {
    // ...
}
```

`subscribedToPrice` 方法可用于判断用户是否基于某个 Paddle 价格 ID 订阅了指定计划。在此示例中，我们将判断用户的 `default` 订阅是否已主动订阅了每月价格（monthly price）：

```php
if ($user->subscribedToPrice($monthly = 'pri_123', 'default')) {
    // ...
}
```

`recurring` 方法可用于判断用户是否当前处于活跃订阅状态，并且**不再**处于试用期或宽限期（grace period）：

```php
if ($user->subscription()->recurring()) {
    // ...
}
```

#### 已取消订阅状态（Canceled Subscription Status）

要判断用户曾经是活跃订阅者但已取消订阅，可以使用 `canceled` 方法：

```php
if ($user->subscription()->canceled()) {
    // ...
}
```

你也可以判断用户是否已取消订阅，但仍处于“宽限期”，直到订阅完全到期。例如，如果用户在 3 月 5 日取消了原定于 3 月 10 日到期的订阅，则该用户在 3 月 10 日之前仍处于“宽限期”。此外，在此期间，`subscribed` 方法仍会返回 `true`：

```php
if ($user->subscription()->onGracePeriod()) {
    // ...
}
```

#### 欠费状态（Past Due Status）

如果订阅付款失败，该订阅将被标记为 `past_due`。当订阅处于此状态时，订阅不会处于活跃状态，直到客户更新付款信息。你可以使用订阅实例的 `pastDue` 方法判断订阅是否处于欠费状态：

```php
if ($user->subscription()->pastDue()) {
    // ...
}
```



当订阅处于欠费（past due）状态时，你应该指示用户 **[更新他们的付款信息](#updating-payment-information)**。

如果你希望在订阅处于 `past_due` 时仍被视为有效，可以使用 Cashier 提供的 `keepPastDueSubscriptionsActive` 方法。通常，该方法应在你的 `AppServiceProvider` 的 `register` 方法中调用：

```php
use Laravel\Paddle\Cashier;

/**
 * 注册任何应用服务。
 */
public function register(): void
{
    Cashier::keepPastDueSubscriptionsActive();
}
```

> [!警告]
> 当订阅处于 `past_due` 状态时，除非更新付款信息，否则无法更改订阅。因此，当订阅处于 `past_due` 状态时，`swap` 和 `updateQuantity` 方法会抛出异常。

#### 订阅查询作用域（Subscription Scopes）

大多数订阅状态也可用作查询作用域（query scopes），以便你可以轻松查询数据库中处于某个状态的订阅：

```php
// 获取所有有效订阅...
$subscriptions = Subscription::query()->valid()->get();

// 获取用户所有已取消的订阅...
$subscriptions = $user->subscriptions()->canceled()->get();
```

以下是可用查询作用域的完整列表：

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

### 订阅单次收费（Subscription Single Charges）

订阅单次收费允许你在订阅基础上向订阅者收取一次性费用。调用 `charge` 方法时，你必须提供一个或多个价格 ID：

```php
// 收取单个价格...
$response = $user->subscription()->charge('pri_123');

// 一次收取多个价格...
$response = $user->subscription()->charge(['pri_123', 'pri_456']);
```



`charge` 方法在**下一个订阅账单周期**到来之前，并不会真正向客户扣费。
如果你希望**立即向客户扣费**，可以改用 `chargeAndInvoice` 方法：

```php
$response = $user->subscription()->chargeAndInvoice('pri_123');
```

### 更新支付信息

Paddle 会为每个订阅保存一个支付方式。
如果你想更新某个订阅的**默认支付方式**，你需要将客户重定向到 Paddle 托管的支付方式更新页面，可以使用订阅模型中的 `redirectToUpdatePaymentMethod` 方法：

```php
use Illuminate\Http\Request;

Route::get('/update-payment-method', function (Request $request) {
    $user = $request->user();

    return $user->subscription()->redirectToUpdatePaymentMethod();
});
```

当用户完成支付信息更新后，Paddle 会发送 `subscription_updated` Webhook，并且你的应用数据库中的订阅信息也会同步更新。

### 更改订阅计划（套餐）

当用户订阅你的应用后，有时可能会希望切换到另一个订阅计划。
要更新用户的订阅计划，你需要将 Paddle 价格（Price）的标识符传递给订阅的 `swap` 方法：


```php
use App\Models\User;

$user = User::find(1);

$user->subscription()->swap($premium = 'pri_456');
```

如果你希望在**切换计划的同时立即生成账单（扣费）**，而不是等待下一个账单周期，可以使用 `swapAndInvoice` 方法：

```php
$user = User::find(1);

$user->subscription()->swapAndInvoice($premium = 'pri_456');
```

#### 费用按比例计算

默认情况下，在不同计划之间切换时，Paddle 会自动**按比例计算差额费用**（Prorate）。
如果你希望**禁用按比例计费**，可以使用 `noProrate` 方法：

```php
$user->subscription('default')->noProrate()->swap($premium = 'pri_456');
```



如果你希望**禁用按比例计费（proration）并立即向客户扣费开具账单**，可以将 `noProrate` 与 `swapAndInvoice` 方法组合使用：

```php
$user->subscription('default')->noProrate()->swapAndInvoice($premium = 'pri_456');
```

或者，如果你希望**在订阅变更时不向客户扣费**，可以使用 `doNotBill` 方法：

```php
$user->subscription('default')->doNotBill()->swap($premium = 'pri_456');
```

有关 Paddle 的按比例计费（proration / 分摊）政策的更多信息，请查阅 Paddle 的 **[proration 文档](https://developer.paddle.com/concepts/subscriptions/proration)**。

### 订阅数量（Subscription Quantity）

有时，订阅会受到“数量（quantity）”的影响。例如，一个项目管理应用可能会按 **每个项目每月 10 美元** 收费。要方便地增加或减少订阅的数量，可以使用 `incrementQuantity`（增加数量）和 `decrementQuantity`（减少数量）方法：

```php
$user = User::find(1);

$user->subscription()->incrementQuantity();

// 在订阅当前数量的基础上增加 5 个...
$user->subscription()->incrementQuantity(5);

$user->subscription()->decrementQuantity();

// 在订阅当前数量的基础上减少 5 个...
$user->subscription()->decrementQuantity(5);
```

或者，你也可以使用 `updateQuantity` 方法设置一个指定的数量：

```php
$user->subscription()->updateQuantity(10);
```

`noProrate` 方法可用于在**不进行按比例计费**（prorate / 分摊费用）的情况下更新订阅数量：

```php
$user->subscription()->noProrate()->updateQuantity(10);
```

#### 多产品订阅的数量操作（Quantities for Subscriptions With Multiple Products）

如果你的订阅是 **[包含多个产品的订阅](#subscriptions-with-multiple-products)**，那么在调用增加/减少数量的方法时，你需要将要操作数量的 price ID 作为第二个参数传入：

```php
$user->subscription()->incrementQuantity(1, 'price_chat');
```

### 多产品订阅（Subscriptions With Multiple Products）

**[多产品订阅](https://developer.paddle.com/build/subscriptions/add-remove-products-prices-addons)** 允许你在同一个订阅下分配多个计费产品（billing products）。
例如，假设你正在构建一个客户服务“帮助台（helpdesk）”应用，它的基础订阅价格是 **每月 10 美元**，同时提供一个 **实时聊天（live chat）附加产品（add-on）**，价格为 **额外每月 15 美元**。
设想你正在构建一个客户服务“帮助台”应用，它的基础订阅价格是每月 10 美元，同时提供一个实时聊天附加产品，价格为额外每月 15 美元。



在创建订阅结账会话时，你可以通过向 `subscribe` 方法的第一个参数传入一个价格数组，来为某个订阅指定多个产品：

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

在上面的示例中，客户的 `default` 订阅下将会关联两个价格。这两个价格将会根据各自的计费周期进行收费。如果需要，你也可以传入一个键/值对应的关联数组，用来指定每个价格对应的具体数量：

```php
$user = User::find(1);

$checkout = $user->subscribe('default', ['price_monthly', 'price_chat' => 5]);
```

如果你想为**已有的订阅**添加另一个价格，则必须使用该订阅的 `swap` 方法。在调用 `swap` 方法时，你也应该同时包含订阅当前已有的价格和对应数量：

```php
$user = User::find(1);

$user->subscription()->swap(['price_chat', 'price_original' => 2]);
```

上面的示例将会添加新的价格，但客户**不会立即被收费**，而是要等到下一个计费周期才会被计费。如果你希望立即向客户收费，可以使用 `swapAndInvoice` 方法：

```php
$user->subscription()->swapAndInvoice(['price_chat', 'price_original' => 2]);
```

你也可以通过使用 `swap` 方法并**省略**你想要移除的价格，来从订阅中移除某个价格：

```php
$user->subscription()->swap(['price_original' => 2]);
```

> [!警告]
> 你不能移除订阅中最后一个价格（the last price on a subscription）。
作为替代，你应该直接取消（cancel）该订阅。


### 多个订阅

Paddle 允许你的客户同时拥有多个订阅。例如，你可能经营一家健身房，提供游泳订阅和举重订阅，并且每个订阅的定价都可能不同。当然，客户应该能够订阅其中一个计划，或同时订阅两个计划。

当你的应用创建订阅时，你可以将订阅类型作为第二个参数提供给 `subscribe` 方法。该类型可以是任何用于表示用户正在启动的订阅类型的字符串：

```php
use Illuminate\Http\Request;

Route::post('/swimming/subscribe', function (Request $request) {
    $checkout = $request->user()->subscribe($swimmingMonthly = 'pri_123', 'swimming');

    return view('billing', ['checkout' => $checkout]);
});
```

在上面的示例中，我们为客户启动了一个按月计费的游泳订阅。不过，客户可能希望在之后的某个时间将其切换为按年计费的订阅。在调整客户的订阅时，我们只需在 `swimming` 订阅上直接更换对应的价格即可：

```php
$user->subscription('swimming')->swap($swimmingYearly = 'pri_456');
```

当然，你也可以将该订阅完全取消：

```php
$user->subscription('swimming')->cancel();
```

### 暂停订阅

要暂停一个订阅，只需调用用户订阅上的 `pause` 方法：

```php
$user->subscription()->pause();
```

当订阅被暂停后，Cashier 会自动在你的数据库中设置 `paused_at` 这一列。该列用于判断 `paused` 方法何时开始返回 `true`。例如，如果客户在3月1日暂停了订阅，但该订阅原定于3月5日才进行下一次续费，那么 `paused` 方法会在3月5日之前继续返回 `false`。这是因为用户通常被允许在当前计费周期结束前继续使用应用。



默认情况下，暂停会在下一个计费周期生效，这样客户可以使用他们已支付的剩余周期。如果你希望立即暂停订阅，可以使用 `pauseNow` 方法：

```php
$user->subscription()->pauseNow();
```

使用 `pauseUntil` 方法，你可以将订阅暂停到指定的时间点：

```php
$user->subscription()->pauseUntil(now()->addMonth());
```

或者，你可以使用 `pauseNowUntil` 方法，将订阅立即暂停直到给定时间：

```php
$user->subscription()->pauseNowUntil(now()->addMonth());
```

你可以使用 `onPausedGracePeriod` 方法判断用户是否已暂停订阅，但仍处于“宽限期”：

```php
if ($user->subscription()->onPausedGracePeriod()) {
    // ...
}
```

要恢复已暂停的订阅，可以在订阅上调用 `resume` 方法：

```php
$user->subscription()->resume();
```

> [!警告]
> 当订阅处于暂停状态时，无法修改订阅。如果你想切换到不同的计划或更新数量，必须先恢复订阅。

### 取消订阅

要取消订阅，可以在用户订阅上调用 `cancel` 方法：

```php
$user->subscription()->cancel();
```

当订阅被取消时，Cashier 会自动在数据库中设置 `ends_at` 这一列。该列用于判断 `subscribed` 方法何时开始返回 `false`。例如，如果客户在 3 月 1 日取消了订阅，但该订阅原定于 3 月 5 日结束，那么在 3 月 5 日之前，`subscribed` 方法仍会返回 `true`。这是因为用户通常被允许在当前计费周期结束前继续使用应用。



你可以使用 `onGracePeriod` 方法来判断用户是否已取消订阅但仍处于宽限期：

```php
if ($user->subscription()->onGracePeriod()) {
    // ...
}
```

如果你希望立即取消订阅，可以在订阅上调用 `cancelNow` 方法：

```php
$user->subscription()->cancelNow();
```

如果要阻止处于宽限期的订阅被取消，可以调用 `stopCancelation` 方法：

```php
$user->subscription()->stopCancelation();
```

> [!警告]
> Paddle 的订阅在取消后无法恢复。如果客户希望重新开通订阅，则必须创建新的订阅。

## 订阅试用

### 预先收集支付方式

如果你希望为客户提供试用期，并提前收集支付方式信息，你需要在 Paddle 控制台中，在客户正在订阅的价格项上设置试用时长。然后像往常一样初始化结账会话

```php
use Illuminate\Http\Request;

Route::get('/user/subscribe', function (Request $request) {
    $checkout = $request->user()
        ->subscribe('pri_monthly')
        ->returnTo(route('home'));

    return view('billing', ['checkout' => $checkout]);
});
```

当你的应用接收到 `subscription_created` 事件时，Cashier 会在你应用的数据库中设置试用期结束日期，并指示 Paddle 在该日期之后才开始扣费。

> [!警告]
> 如果客户的订阅在试用期结束日期之前未被取消，则会在试用期到期后立即被扣费，因此你必须确保及时通知用户试用结束时间。



你可以在用户实例上使用 `onTrial` 方法来判断用户是否处于试用期：

```php
if ($user->onTrial()) {
    // ...
}
```

要判断现有试用是否已经过期，可以使用 `hasExpiredTrial` 方法：

```php
if ($user->hasExpiredTrial()) {
    // ...
}
```

要判断用户是否处于某种特定订阅类型的试用期，可以向 `onTrial` 或 `hasExpiredTrial` 方法传入订阅类型：

```php
if ($user->onTrial('default')) {
    // ...
}

if ($user->hasExpiredTrial('default')) {
    // ...
}
```

### 不提前收集支付方式

如果你希望在不提前收集用户支付方式信息的情况下提供试用期，你可以在与你的用户关联的客户记录上设置 `trial_ends_at` 字段为你想要的试用结束日期。这个设置通常会在用户注册时完成：

```php
use App\Models\User;

$user = User::create([
    // ...
]);

$user->createAsCustomer([
    'trial_ends_at' => now()->addDays(10)
]);
```

Cashier 将这种试用称为通用试用，因为它没有绑定到任何已有的订阅。
如果当前日期还没有超过 `trial_ends_at` 的时间值，那么 `User` 实例上的 `onTrial` 方法会返回 `true`：

```php
if ($user->onTrial()) {
    // 用户处于试用期内...
}
```

当你准备为用户创建真正的订阅时，可以像往常一样调用 `subscribe` 方法：

```php
use Illuminate\Http\Request;

Route::get('/user/subscribe', function (Request $request) {
    $checkout = $request->user()
        ->subscribe('pri_monthly')
        ->returnTo(route('home'));

    return view('billing', ['checkout' => $checkout]);
});
```

要获取用户的试用结束日期，你可以使用 `trialEndsAt` 方法。
如果用户正在试用，该方法会返回一个 Carbon 日期实例，否则返回 `null`。
如果你希望获取默认订阅之外的某个特定订阅的试用结束日期，也可以向该方法传入订阅类型参数：

```php
if ($user->onTrial('default')) {
    $trialEndsAt = $user->trialEndsAt();
}
```



如果你想明确判断用户正处于通用试用期，并且**尚未创建真实订阅**，可以使用 `onGenericTrial` 方法：

```php
if ($user->onGenericTrial()) {
    // 用户正处于通用试用期内……
}
```

### 延长或激活试用期

你可以在已有订阅上调用 `extendTrial` 方法来延长当前的试用期，并指定试用应当结束的具体时间：

```php
$user->subscription()->extendTrial(now()->addDays(5));
```

或者，你也可以通过在订阅上调用 `activate` 方法来**立即激活订阅并提前结束试用期**：

```php
$user->subscription()->activate();
```

## 处理 Paddle Webhook

Paddle 会通过 webhook 通知你的应用各种事件。默认情况下，Cashier 服务提供者已经注册了指向 Cashier webhook 控制器的路由，该控制器会处理所有传入的 webhook 请求。

这个控制器默认会自动处理**扣费失败次数过多导致的订阅取消、订阅更新以及支付方式变更**；不过，后续你也可以扩展该控制器，让它支持处理你需要的任何 Paddle webhook 事件。

为了确保你的应用可以正常接收 webhook，你需要先在 [Paddle 控制面板](https://vendors.paddle.com/alerts-webhooks) 中配置 webhook 地址。Cashier 的 webhook 控制器默认响应的路径是 `/paddle/webhook`，你需要在控制面板中启用的 webhook 事件包括：

-   客户信息更新
-   交易完成
-   交易更新
-   订阅创建
-   订阅更新
-   订阅暂停
-   订阅取消

> [!警告]
> 记得使用 Cashier 提供的 [webhook 签名验证中间件](/docs/laravel/12.x/cashier-paddle#verifying-webhook-signatures) 来保护传入请求，确保安全性。



#### Webhook 与 CSRF 保护

由于 Paddle webhook 需要绕过 Laravel 的 [CSRF 保护](/docs/laravel/12.x/csrf)，你需要确保 Laravel 不会尝试验证传入的 Paddle webhook 的 CSRF token。为此，你应当在应用的 `bootstrap/app.php` 文件中将 `paddle/*` 排除在 CSRF 保护之外：

```php
->withMiddleware(function (Middleware $middleware) {
    $middleware->validateCsrfTokens(except: [
        'paddle/*',
    ]);
})
```
#### Webhook 与本地开发

为了让 Paddle 能够在本地开发期间向你的应用发送 webhook，你需要通过类似 [Ngrok](https://ngrok.com/) 或 [Expose](https://expose.dev/docs/introduction) 的站点共享服务暴露你的应用。如果你使用 [Laravel Sail](/docs/laravel/12.x/sail) 进行本地开发，也可以使用 Sail 提供的 [站点共享命令](/docs/laravel/12.x/sail#sharing-your-site)。

### 定义 Webhook 事件处理器

Cashier 会自动处理因扣费失败而取消订阅以及其他常见的 Paddle webhook 事件。但是，如果你有额外的 webhook 事件需要处理，也可以通过监听 Cashier 派发的以下事件来实现：

-   `Laravel\Paddle\Events\WebhookReceived`

-   `Laravel\Paddle\Events\WebhookHandled`

这两个事件都包含 Paddle webhook 的完整 payload。例如，如果你想处理 `transaction.billed` webhook，可以注册一个 [监听器](/docs/laravel/12.x/events#defining-listeners) 来处理该事件：

```php
<?php

namespace App\Listeners;

use Laravel\Paddle\Events\WebhookReceived;

class PaddleEventListener
{
    /**
     * 处理接收到的 Paddle webhook
     */
    public function handle(WebhookReceived $event): void
    {
        if ($event->payload['event_type'] === 'transaction.billed') {
            // 处理传入的事件...
        }
    }
}
```



Cashier 还会根据接收到的 webhook 类型触发专门的事件。除了包含来自 Paddle 的完整 payload，这些事件还包含用于处理 webhook 的相关模型，例如可计费模型、订阅或收据：

<div class="content-list" markdown="1">

- `Laravel\Paddle\Events\CustomerUpdated`
- `Laravel\Paddle\Events\TransactionCompleted`
- `Laravel\Paddle\Events\TransactionUpdated`
- `Laravel\Paddle\Events\SubscriptionCreated`
- `Laravel\Paddle\Events\SubscriptionUpdated`
- `Laravel\Paddle\Events\SubscriptionPaused`
- `Laravel\Paddle\Events\SubscriptionCanceled`

</div>

你也可以通过在应用的 `.env` 文件中定义 `CASHIER_WEBHOOK` 环境变量来覆盖默认的内置 webhook 路由。该值应为你 webhook 路由的完整 URL，并且需要与 Paddle 控制面板中设置的 URL 相匹配：

```ini
CASHIER_WEBHOOK=https://example.com/my-paddle-webhook-url
```

### 验证 Webhook 签名

为了保护你的 webhook，可以使用 [Paddle 的 webhook 签名](https://developer.paddle.com/webhook-reference/verifying-webhooks)。为了方便，Cashier 自动包含了一个中间件，用于验证传入的 Paddle webhook 请求是否合法。

要启用 webhook 验证，请确保在应用的 `.env` 文件中定义了 `PADDLE_WEBHOOK_SECRET` 环境变量。该 webhook 密钥可以从你的 Paddle 账户控制面板获取。

## 单次收费

### 商品购买收费

如果你希望为客户发起商品购买，可以在可计费模型实例上使用 `checkout` 方法生成购买的结账会话。`checkout` 方法可以接受一个或多个价格 ID。如果需要，也可以使用关联数组来提供购买商品的数量：

```php
use Illuminate\Http\Request;

Route::get('/buy', function (Request $request) {
    $checkout = $request->user()->checkout(['pri_tshirt', 'pri_socks' => 5]);

    return view('buy', ['checkout' => $checkout]);
});
```



在生成结账会话之后，你可以使用 Cashier 提供的 `paddle-button` [Blade 组件](#overlay-checkout)，让用户查看 Paddle 结账小部件并完成购买：

```blade
<x-paddle-button :checkout="$checkout" class="px-8 py-4">
    Buy
</x-paddle-button>
```

结账会话具有一个 `customData` 方法，允许你将任何你希望的自定义数据传递给底层的交易创建过程。请查阅 [Paddle 文档](https://developer.paddle.com/build/transactions/custom-data)，以了解在传递自定义数据时可用的选项：

```php
$checkout = $user->checkout('pri_tshirt')
    ->customData([
        'custom_option' => $value,
    ]);
```

### 退款交易

退款交易会将退款金额退回到客户在购买时所使用的支付方式。如果你需要对一次 Paddle 购买进行退款，可以在 `Cashier\Paddle\Transaction` 模型上使用 `refund` 方法。该方法将退款原因作为第一个参数，并接受一个或多个价格 ID（可选地附带金额）的关联数组。你可以使用 `transactions` 方法来获取某个可计费模型的交易记录。

例如，假设我们想要为价格 `pri_123` 和 `pri_456` 退款一笔特定的交易。我们希望对 `pri_123` 进行全额退款，但只对 `pri_456` 退款两美元：

```php
use App\Models\User;

$user = User::find(1);

$transaction = $user->transactions()->first();

$response = $transaction->refund('Accidental charge', [
    'pri_123', // 全额退款该价格项……
    'pri_456' => 200, // 仅对该价格项进行部分退款……
]);
```

上面的示例对交易中的特定行项目进行了退款。如果你想要退款整个交易，只需提供退款原因即可：

```php
$response = $transaction->refund('Accidental charge');
```



有关退款的更多信息，请查阅 [Paddle 的退款文档](https://developer.paddle.com/build/transactions/create-transaction-adjustments)。

> [!警告]
> 退款在完全处理之前，必须始终经过 Paddle 的批准。

### 交易入账（Crediting Transactions）

与退款类似，你也可以对交易进行入账操作。交易入账会将资金添加到客户的余额中，以便其用于未来的购买。交易入账只能用于**手动收款的交易**，而不能用于**自动收款的交易**（例如订阅），因为 Paddle 会自动处理订阅的入账：

```php
$transaction = $user->transactions()->first();

// 对某个特定的行项目进行全额入账……
$response = $transaction->credit('Compensation', 'pri_123');
```

更多信息请参阅 [Paddle 关于交易入账的文档](https://developer.paddle.com/build/transactions/create-transaction-adjustments)。

> [!警告]
> 入账操作只能应用于手动收款的交易。自动收款的交易将由 Paddle 自行进行入账处理。

## 交易（Transactions）

你可以通过 `transactions` 属性，轻松地获取某个可计费模型的交易数组：

```php
use App\Models\User;

$user = User::find(1);

$transactions = $user->transactions;
```

$transactions = $user->transactions;

交易表示你产品和购买行为的付款记录，并且会附带发票。只有已完成的交易才会被存储在你应用程序的数据库中。

在为客户列出交易记录时，你可以使用交易实例的方法来显示相关的付款信息。例如，你可能希望在一个表格中列出每一笔交易，以便用户能够轻松下载对应的发票：

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



`download-invoice` 路由可能如下所示：

```php
use Illuminate\Http\Request;
use Laravel\Paddle\Transaction;

Route::get('/download-invoice/{transaction}', function (Request $request, Transaction $transaction) {
    return $transaction->redirectToInvoicePdf();
})->name('download-invoice');
```

### 过往与即将到来的付款

你可以使用 `lastPayment` 和 `nextPayment` 方法，来获取并展示客户在周期性订阅中的过往付款或即将到来的付款：

```php
use App\Models\User;

$user = User::find(1);

$subscription = $user->subscription();

$lastPayment = $subscription->lastPayment();
$nextPayment = $subscription->nextPayment();
```

这两个方法都会返回一个 `Laravel\Paddle\Payment` 实例；不过，当交易尚未通过 Webhook 同步完成时，`lastPayment` 将返回 `null`，而当计费周期已经结束时（例如订阅已被取消），`nextPayment` 将返回 `null`：

```blade
Next payment: {{ $nextPayment->amount() }} due on {{ $nextPayment->date()->format('d/m/Y') }}
```

## 测试

在测试过程中，你应该手动测试你的计费流程，以确保你的集成能够按预期工作。

对于自动化测试（包括在 CI 环境中执行的测试），你可以使用 [Laravel 的 HTTP 客户端](/docs/laravel/12.x/http-client#testing) 来伪造（fake）对 Paddle 发起的 HTTP 调用。尽管这并不会测试 Paddle 的真实响应，但它确实提供了一种在不实际调用 Paddle API 的情况下测试你的应用程序的方法。
