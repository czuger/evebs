class Setup::CppSourcesIndustryActivityProduct < ActiveRecord::Base

  self.table_name = 'industryActivityProducts'

  establish_connection :cpp_original_data

end