class Setup::CppSourcesMarketGroup < ActiveRecord::Base

  self.table_name = 'invMarketGroups'

  establish_connection :cpp_original_data

end