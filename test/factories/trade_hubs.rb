FactoryGirl.define do
  factory :trade_hub do
    region
    factory :rens do
      eve_system_id '30002510'
      name "Rens"
    end
  end
end
