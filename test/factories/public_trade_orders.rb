FactoryBot.define do
  factory :public_trade_order do
    order_id { 1 }
    is_buy_order { false }
    end_time { Time.now + 3600 }
    price { 50 }
    range { :region }
    volume_remain { 5000 }
    volume_total{ 10000 }
    min_volume { 50 }
    touched { false }
  end
end
