class Setup::CppSourcesEveItem < ApplicationRecord

  self.table_name = 'invTypes'

  establish_connection :cpp_original_data

end