FactoryBot.define do
  factory :eve_market_history_archive do
    region_id 1
    eve_item_id 1
    year 1
    month 1
    history_date "2018-04-26"
    order_count 1
    volume 1
    low_price 1.5
    avg_price 1.5
    high_price 1.5
  end
end
