class Setup::CppSourcesEveItem < ActiveRecord::Base

  self.table_name = 'invTypes'

  establish_connection :cpp_original_data

end