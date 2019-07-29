FactoryBot.define do
  factory :trade_volume_estimation do
    universe_stations { nil }
    eve_items { nil }
    day_timestamp { "MyString" }
    volume_total_sum { "" }
    volume_percent { 1.5 }
  end
end
