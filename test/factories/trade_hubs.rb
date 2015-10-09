FactoryGirl.define do

  factory :trade_hub do

    factory :rens do
      eve_system_id '30002510'
      name "Rens"
    end

    factory :pator do
      eve_system_id '30002544'
      name "Pator"
    end

    factory :amarr do
      eve_system_id '30002187'
      name "Amarr"
    end

  end

end
