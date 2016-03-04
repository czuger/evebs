class Setup::CppSourcesIndustryBlueprint < ActiveRecord::Base

  self.table_name = 'industryBlueprints'

  has_many :products, -> { where activityID: 1 }, class_name: 'CppSourcesIndustryActivityProduct', primary_key: 'typeID', foreign_key: 'typeID'
  has_many :materials, -> { where activityID: 1, consume: 1 }, class_name: 'CppSourcesIndustryActivityMaterial', primary_key: 'typeID', foreign_key: 'typeID'

  establish_connection :cpp_original_data

end