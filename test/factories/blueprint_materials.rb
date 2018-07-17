FactoryBot.define do
  factory :blueprint_material do

    factory :material_morphite do

      blueprint { FactoryBot.create( :blueprint ) }
      blueprint_component { FactoryBot.create( :component_morphite ) }

      required_qtt 15
    end
  end
end
