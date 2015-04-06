class OrdersAdvicesController < ApplicationController
  def index
    @order_advices = OrderAdvices.do
  end
end
