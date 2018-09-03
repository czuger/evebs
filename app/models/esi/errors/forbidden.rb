module Esi::Errors
  class Forbidden < Base

    def error_hook
      exit
    end

  end
end
