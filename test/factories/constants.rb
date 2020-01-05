FactoryBot.define do
  factory :constant do
    factory :taxes do
      libe { 'taxes' }
      f_value { 1.5 }
      description { 'taxes description' }
    end
  end
end
