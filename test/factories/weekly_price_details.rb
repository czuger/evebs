FactoryBot.define do
  factory :weekly_price_detail do
    eve_item { nil }
    day { "2018-10-01" }
    volume { 1.5 }
    weighted_avg_price { 1.5 }
  end
end
