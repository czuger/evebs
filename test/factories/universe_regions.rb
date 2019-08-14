FactoryBot.define do
  factory :universe_region do

    cpp_region_id {'123456'}
    name {'Region test'}

    factory :universe_the_forge do
      cpp_region_id {'10000002'}
      name {'The Forge'}
    end

  end

end
