FactoryBot.define do
  factory :eve_market_history do
    volume { 1000 }
    highest { 50.5 }
    lowest { 3.5 }
    average { 25.5 }
    order_count { 457789 }
  end
end
