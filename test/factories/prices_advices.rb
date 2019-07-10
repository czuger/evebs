FactoryBot.define do
  factory :prices_advice do
    vol_month { 5000000 }
    avg_price_month { 50 }
    immediate_montly_pcent { 0.3 }
    margin_percent { 0.5 }
    avg_price_week { 70 }
  end
end
