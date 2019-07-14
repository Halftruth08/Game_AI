(ns codenames-clj.core
  (:require [clojure.java.io :as io]
            [clojure.string :as string]
            [codenames-clj.model :as mdl]
            [codenames-clj.storage :as store]
            [codenames-clj.game :as game])
  (:gen-class))





;(def model1 (io/resource "models/model1.txt"))


  


  
(defn -main
  "I don't do a whole lot ... yet."
  [& args]
  (println "Hello, World!")

  ;(println codenames-get)
  ;(println (vec (repeat 25 number-of-codenames)))
  (let [wl1 (game/gen-wordlist)]
    (println wl1)
    (println (- 9 1))
    (println (game/get-wordlist-words wl1))
    ;(println (subvec (get-wordlist-words wl1) 0 5))
    (game/show-gameboard (game/get-wordlist-words wl1))
  ;(println (first mdl/model-files))
  ;(doseq [x (take 25 (mdl/model))] (println x))
   (let [mod1 (if (.exists (io/as-file "resources/models/model1.txt")) 
                (mdl/generate-all-models [["models/model1.txt" 1]]) 
                mdl/model)
         out "resources/models/test.txt"]
    (println (type mod1))
    (doseq [x (take 5 mod1)] (game/entry-words x))
    (doseq [x (take 5 (keys mod1))] (println x))
    (doseq [x (take 5 (keys (first (vals mod1))))] (println x))
    (println (type (first (vals mod1))))
    (def modc (game/compact game/codenames mod1))
    (doseq [x (take 1 modc)] (println x))
    (def modr (game/reverse-hash modc))
    (doseq [x (take 1 modr)] (println x))
    (def modrc (game/compact game/codenames modr))
    (doseq [x (take 1 modrc)] (println x))
      ;(println (store/entry "word" "weight" "leaf"))
      ;(spit out (string/join "\n" (take 5 (keys (first (vals mod1)))))))
    (if (.exists (io/as-file "resources/models/model1c.txt")) 
      (doseq [x (take 1 modc)] (println x))
      (store/model-save "model1c.txt" modc))
    (if (.exists (io/as-file "resources/models/model1r.txt")) 
      (doseq [x (take 1 modr)] (println x))
      (store/model-save "model1r.txt" modr))
    (if (.exists (io/as-file "resources/models/model1rc.txt")) 
      (doseq [x (take 1 modrc)] (println x))
      (store/model-save "model1rc.txt" modrc))
    (let [modb (mdl/generate-all-models [["models/model1c.txt" 1]
                                         ["models/model1rc.txt" 1]])]
     (doseq [x (take 5 modb)] (println x))
     (if (.exists (io/as-file "resources/models/model1b.txt")) 
      (doseq [x (take 5 modb)] (println x))
      (store/model-save "model1b.txt" modb)))))
     
  ;(store/model-save "model1.txt" mdl/model))
  

  ;(if (.exists (io/as-file "model1.txt"))  (println (take 5 (mdl/model))) (println (take 3 (mdl/model)))))
  
  
  (println (first mdl/model-files)))
