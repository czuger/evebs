FactoryBot.define do
  factory :public_trade_order do
    trade_hub nil
    eve_item nil
    order_id ""
    is_buy_order false
    end_time "2018-09-06 15:11:40"
    price 1.5
    range "MyString"
    volume_remain ""
    volume_total ""
    min_volume ""
  end
end
