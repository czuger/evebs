FactoryBot.define do
  factory :weekly_price_detail do
    day { "2018-10-01" }
    volume { 1.5 }
    weighted_avg_price { 67.8 }
  end
end
