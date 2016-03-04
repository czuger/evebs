class Setup::CppSourcesIndustryActivityMaterial < ActiveRecord::Base

  self.table_name = 'industryActivityMaterials'

  establish_connection :cpp_original_data

end