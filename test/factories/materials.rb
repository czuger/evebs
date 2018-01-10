FactoryBot.define do
  factory :material do
    factory :material_morphite do
      component {FactoryBot.create( :component_morphite )}
      required_qtt 15
    end
    factory :material_rocket_fuel do
      component {FactoryBot.create( :component_rocket_fuel )}
      required_qtt 129
    end
    factory :material_ram_amunition_tech do
      component {FactoryBot.create( :component_ram_amunition_tech )}
      required_qtt 1
    end
    factory :material_plasma_pulse_generator do
      component {FactoryBot.create( :component_plasma_pulse_generator )}
      required_qtt 14
    end
    factory :material_phenolic_composite do
      component {FactoryBot.create( :component_phenolic_composite )}
      required_qtt 59
    end
  end
end
