FactoryBot.define do

  factory :trade_hub do

    eve_system_id '123456'
    name 'Test trade hub'

    factory :jita do
      eve_system_id '30000142'
      name 'Jita'
      region { create( :the_forge ) }
    end

    factory :rens do
      eve_system_id '30002510'
      name 'Rens'
    end

    factory :pator do
      eve_system_id '30002544'
      name 'Pator'
    end

    factory :amarr do
      eve_system_id '30002187'
      name 'Amarr'
    end

    factory :e02_ik do
      id 15
      eve_system_id '30000903'
      name 'E02-IK'
    end

  end

end
