from util import *


def algorithm(K, all_orders, all_riders, dist_mat, timelimit=60):

    start_time = time.time()

    for r in all_riders:
        r.T = np.round(dist_mat/r.speed + r.service_time)

    # A solution is a list of bundles
    solution = []

    #------------- Custom algorithm code starts from here --------------#

    # Step 0: Generate initial bundles using random merge algorithm
    car_rider = None
    for r in all_riders:
        if r.type == 'CAR':
            car_rider = r
        if r.type == 'WALK':
            walk_rider = r
        if r.type == 'BIKE':
            bike_rider = r

    all_bundles = []

    for ord in all_orders:
        new_bundle = Bundle(all_orders, car_rider, [ord.id], [ord.id], ord.volume, dist_mat[ord.id, ord.id + K])
        all_bundles.append(new_bundle)
        car_rider.available_number -= 1

    best_obj = sum((bundle.cost for bundle in all_bundles)) / K
    print(f'Initial Best obj = {best_obj}')

    iter = 0
    max_merge_iter = 1000

    while time.time() - start_time < 10 and iter < max_merge_iter:
        if time.time() - start_time >= timelimit:
            solution = [
                [bundle.rider.type, bundle.shop_seq, bundle.dlv_seq]
                for bundle in all_bundles
            ]
            return solution

        bundle1, bundle2 = select_two_bundles(all_bundles)
        new_bundle = try_merging_bundles(K, dist_mat, all_orders, bundle1, bundle2)

        if new_bundle is not None:
            all_bundles.remove(bundle1)
            bundle1.rider.available_number += 1

            all_bundles.remove(bundle2)
            bundle2.rider.available_number += 1

            all_bundles.append(new_bundle)
            new_bundle.rider.available_number -= 1

            cur_obj = sum((bundle.cost for bundle in all_bundles)) / K
            if cur_obj < best_obj:
                best_obj = cur_obj

        iter += 1
    
    print(f'휴리스틱 전 초기해 obj = {best_obj}')

    #용량, 가능 수 고려 rider 지정
    # rider 지정 시 available_number 수정 요함
    def vrp(all_orders, K, dist_mat, bundle, rider):

        best_bundle = None

        for shop_perm in permutations(bundle.shop_seq):
            for dlv_perm in permutations(bundle.dlv_seq):
                if test_route_feasibility(all_orders, rider, shop_perm, dlv_perm) == 0: #feasible
                    total_dist = get_total_distance(K, dist_mat, shop_perm, dlv_perm)
                    new_bundle = Bundle(all_orders, rider, list(shop_perm), list(dlv_perm), bundle.total_volume, total_dist)

                    new_bundle_cost = rider.calculate_cost(total_dist)
                else:
                    continue

                if best_bundle is None:
                    best_bundle = new_bundle
                    best_bundle_cost = new_bundle_cost

                elif new_bundle_cost < best_bundle_cost:
                    best_bundle = new_bundle
                    best_bundle_cost = new_bundle_cost                
        
        return best_bundle
    #vrp함수 infeasible하면 None, feasible하면 optimal_bundle 반환
    #feasible rider input 해주기
    # after bundle의 rider가 달라졌다면 rider 수 조정 밖에서 해주기
    
    # bundle의 초기값 저장 (before_cost)
    # bundle의 각 order에 대한 반복문 시작
    # bundle에서 해당 order를 제외하고 routing을 진행한 cost와 해당 단일 order의 cost를 더하여 after_cost로 저장
    # 이때 routing은 vrp함수를 사용. 단일 order의 rider는 car로 지정
    # before_cost에서 after_cost를 뺀 값을 delta_cost로 저장
    # 반복문의 결과에서 가장 delta_cost 가 최대가 되는 경우의 단일번들, 단일번들을 제외한 bundle, delta_cost을 반환
    def opt_devide(bundle):
        best_single_order_bundle = None
        best_remaining_bundle = None
        best_delta_cost = float('-inf')

        before_cost = bundle.cost

        for order_id in bundle.shop_seq:
            remaining_orders = [ord for ord in bundle.shop_seq if ord != order_id]

            #remainging_bundle은 같은 rider로, single_order_bundle은 car_rider로
            remaining_bundle = vrp(all_orders, K, dist_mat, Bundle(all_orders, bundle.rider, remaining_orders, remaining_orders, get_total_volume(all_orders, remaining_orders), get_total_distance(K, dist_mat, remaining_orders, remaining_orders)), bundle.rider)
            single_order_bundle = Bundle(all_orders, car_rider, [order_id], [order_id], all_orders[order_id].volume, dist_mat[order_id, order_id + K])

            #누굴 뽑느냐에 따라 remainging_bundle.cost값이 달라-> vrp 필요함
            after_cost = remaining_bundle.cost + single_order_bundle.cost
            delta_cost = before_cost - after_cost

            if delta_cost > best_delta_cost:
                best_delta_cost = delta_cost
                best_single_order_bundle = single_order_bundle
                best_remaining_bundle = remaining_bundle
    
        return best_single_order_bundle, best_remaining_bundle, best_delta_cost

    # 해당 bundle에서 랜덤한 분해를 진행

    # bundle의 초기값 저장 (before_cost)
    # bundle에서 랜덤한 하나의 order를 제외하여 단일번들로 지정
    # bundle에서 해당 order를 제외하고 routing을 진행한 cost와 해당 단일 order의 cost를 더하여 after_cost로 저장
    # 이때 routing은 vrp함수를 사용. 단일 order의 rider는 car로 지정
    # before_cost에서 after_cost를 뺀 값을 delta_cost로 저장
    # 단일번들, 단일번들을 제외한 bundle, delta_cost을 반환
    def rand_devide(bundle):
        order_id = random.choice(bundle.shop_seq)
        remaining_orders = [ord for ord in bundle.shop_seq if ord != order_id]

        before_cost = bundle.cost

        remaining_bundle = vrp(all_orders, K, dist_mat, Bundle(all_orders, bundle.rider, remaining_orders, remaining_orders, get_total_volume(all_orders, remaining_orders), get_total_distance(K, dist_mat, remaining_orders, remaining_orders)), bundle.rider)
        single_order_bundle = Bundle(all_orders, car_rider, [order_id], [order_id], all_orders[order_id].volume, dist_mat[order_id, order_id + K])

        after_cost = remaining_bundle.cost + single_order_bundle.cost
        delta_cost = before_cost - after_cost
    
        return single_order_bundle, remaining_bundle, delta_cost


    ##############################GREEDY_DIVIDE_MERGE################################
    # 상수 설명 0=< k1, k2, k3 <=1
    # k1 = step1(devide)에서 greedy 쓸 비율
    # k2 = step2(Single_Order)에서 greedy 쓸 비율
    # k3 = step3(Original_Single_Order)에서 greedy 쓸 비용
    def greedy_dv_mg(all_bundles,k1=0.9,k2=0.9,k3=0.9):

        Multi_Order = [bundle for bundle in all_bundles if len(bundle.shop_seq) > 1]
        Original_Single_Order = [bundle for bundle in all_bundles if len(bundle.shop_seq) == 1]
        Single_Order = []
        Single_Cost = []

        # 업데이트용 임시리스트
        after_multi = []
        

        # Multi_Order의 각 bundle에 대한 반복문 시작

        # 각 bundle에서 80%로 opt_devide, 20%로 rand_devide를 진행
        # 기존 bundle을 반환된 bundle로 대체하고 Single_order에 반환된 단일 번들을 추가, Single_Cost에 반환된 delta_cost를 추가
        for bundle in Multi_Order:
            if random.random() < k1 :
                single_order_bundle, remaining_bundle, delta_cost = opt_devide(bundle)
            else:
                single_order_bundle, remaining_bundle, delta_cost = rand_devide(bundle)

            # 요거 all_bundle에 반영 안해도 되나? <- 고민좀 해봄.... _아직 안해도 될것 같음_원준
            # all_bundles.remove(bundle)
            # bundle.rider.available_number += 1

            # Multi_Order에 주문 1개가 제외된 번들 추가 (루프문 안꼬이게 임시 리스트에 저장)
            after_multi.append(remaining_bundle)
            # remaining_bundle.rider.available_number -= 1
            # bundle과 remaining_bundle은 같은 rider 사용해서 상쇄됨

            # Single_Order에 제외된 단일 번들 추가
            Single_Order.append(single_order_bundle)
            Single_Cost.append(delta_cost)
            single_order_bundle.rider.available_number -= 1
            #car rider 수 내려감

        # delta_cost에 대한 오름차순으로 Single_order를 정렬
        Single_Order = [x for _, x in sorted(zip(Single_Cost, Single_Order), key=lambda item: item[0])]

        # Multi_Order 초기화하고, remaining_bundle 리스트(after_multi)로 치환
        Multi_Order = []
        #Multi_Order.extend(after_multi)
        #Multi_Order 길이가 두개였던 애들은 remaining_bundle이 1개 order일텐데, muti에 걍 넣어도 되나,,? 
        # 안됨!! original single에 넣어야돼
        for bundle in after_multi:
            if len(bundle.shop_seq) > 1:
                Multi_Order.append(bundle)
            else:
                Original_Single_Order.append(bundle)

        # 여기까지 각각 리스트 정의 완료

        # print("step1 이상무!!!!!!")
        
        ############################Step2 하나씩 넣기################################

        ##Greedy Merge!!
        # MO, OSO, SO는 각각 Bundle 객체들의 리스트
        #아직 all_bundles에 적용 안됨.
        #rider는 적용중
        
        MOS= [Multi_Order, Original_Single_Order, Single_Order]

        def combine(all_orders, all_riders, dist_mat, bundle1, bundle2):
            initial_cost = bundle1.cost + bundle2.cost
            merged_orders = bundle1.shop_seq + bundle2.shop_seq
            total_volume = get_total_volume(all_orders, merged_orders)
            total_dist = get_total_distance(K,dist_mat,merged_orders,merged_orders)

            bundle1.rider.available_number +=1
            bundle2.rider.available_number +=1
            
            feasible_riders = [r for r in all_riders if r.capa >= total_volume and r.available_number > 0]
            best_bundle = None

            # We skip the test if there are too many orders
            if len(merged_orders) <= 5:
                for fr in feasible_riders: #사실상 bike와 car의 비교
                    new_bundle = vrp(all_orders, K, dist_mat, Bundle(all_orders, fr, merged_orders,merged_orders, total_volume, total_dist), fr)
                    if new_bundle : #feasible한 rider와 routing이 있다면
                        if best_bundle is None or new_bundle.cost < best_bundle.cost: # 사실상 bike와 car중 cost 낮은애로 업데이트
                                best_bundle = new_bundle
            
            bundle1.rider.available_number -= 1
            bundle2.rider.available_number -= 1

            #Step2에서 initial cost를 굳이 고려 안하고 있잖아!
            # if best_bundle and best_bundle.cost < initial_cost:
            #     return best_bundle
            
            return best_bundle
        #rider와 routing이 전부 infeasible하면 None 반환
        #사용시 new_bundle=combine( )으로 사용하고, new_bunlde 이 not none 일때, rider 수 조정 필요
        #combine함수에서 두 번들을 합치기 전에 각 번들의 rider도 고려해줘야 하기때문에 
        #두 번들의 각 rider들의 available_number를 잠깐 올려준 후 vrp 돌려보고, 함수 끝나기 전에 다시 내려준다
        #결국은 combine 사용할때는 rider 수 조정이 필요하다
        #     

        #Single_Order에 들어있던 모든 주문들 greedy하게 best_bundle 뽑고 
        # 합쳐서 multi에 넣음 (거의 없는 예외: 전부 infeas하면 걍 냅둠)
        for i in range(len(Single_Order)):
            best_merge = None
            best_cost_reduction = float('-inf') #cost를 낮추는 bundle 조합이 없어도 feasible만 하면 그중 젤 나은애로 combine
            cost_reduction = None

            current_order = Single_Order[i]
            # 무작위 탐색 1-k %의 확률
            if random.random() < 1-k2 :
                # 무작위로 번들을 선택하여 합치기
                if i+1 < len(Single_Order):
                    potential_bundles = Multi_Order + Original_Single_Order + Single_Order[i+1:]
                else:
                    potential_bundles = Multi_Order + Original_Single_Order

                random.shuffle(potential_bundles)  # 번들을 무작위로 섞기
                for potential_bundle in potential_bundles:
                    merged_bundle = combine(all_orders, all_riders, dist_mat, potential_bundle, current_order)
                    if merged_bundle:
                        best_merge = (current_order, potential_bundle, merged_bundle)
                        break  # 무작위로 첫 feasible한 번들을 찾으면 합치기
                    

            else: # k%
                # greedy하게 모든 경우 보면서 best_merger 번들 찾아 결합
                for MO in Multi_Order: #Multi_Order 싹 훑기
                    merged_bundle = combine(all_orders, all_riders, dist_mat, MO, current_order)
                    if merged_bundle: #merged_bundle이 not None일때,
                        cost_reduction = MO.cost + current_order.cost - merged_bundle.cost
                        if cost_reduction > best_cost_reduction:
                            best_cost_reduction = cost_reduction
                            best_merge = (current_order, MO, merged_bundle)
                for OSO in Original_Single_Order: #Original_Single_Order 싹 훑기
                    merged_bundle = combine(all_orders, all_riders, dist_mat, OSO, current_order)
                    if merged_bundle: #merged_bundle이 not None일때,
                        cost_reduction = OSO.cost + current_order.cost - merged_bundle.cost
                        if cost_reduction > best_cost_reduction:
                            best_cost_reduction = cost_reduction
                            best_merge = (current_order, OSO, merged_bundle)
                if i+1 < len(Single_Order):
                    for other_order in Single_Order[i+1:]: #나머지 Single_Order 들도 싹 훑기
                        merged_bundle = combine(all_orders, all_riders, dist_mat, other_order, current_order)
                        if merged_bundle: # merged_bundle이 not None일 때,
                            cost_reduction = other_order.cost + current_order.cost - merged_bundle.cost
                            if cost_reduction > best_cost_reduction:
                                best_cost_reduction = cost_reduction
                                best_merge = (current_order, other_order, merged_bundle)
                
            if best_merge: #combine되는 feasible한 bundle이 있음(cost 나옴)
                best_merger = best_merge[1] #합치는 bundle중 젤 좋은애
                merge_bundle = best_merge[2] #그래서 합친 bundle

                car_rider.available_number += 1 # car 사용하던 Single_Order의 rider +1
                best_merger.rider.available_number += 1 # 합치는 상대 bundle rider +1

                merge_bundle.rider.available_number -=1 #새로 생긴 bundle의 rider -1

                # best_merger가 어느 리스트에 있는지 확인 후 삭제
                if best_merger in Multi_Order:
                    Multi_Order.remove(best_merger)
                elif best_merger in Original_Single_Order:
                    Original_Single_Order.remove(best_merger)
                elif best_merger in Single_Order:
                    Single_Order.remove(best_merger)

                # 병합된 번들을 Multi_Order에 추가
                Multi_Order.append(merge_bundle)

            else:  # 가능한 bundle 조합이 없는 경우 #거의 없겠지만 안전장치
                print(f'{Single_Order[i].shop_seq}는 다른 bundle과 전부 infeasible')
                Multi_Order.append(current_order)

            Single_Order[i] = None #None값으로 바꿔줌
            if i == len(Single_Order)-1 :
                break

        # Single_Order 리스트 체크
        if any(order is not None for order in Single_Order):
            print("error: Single_Order 리스트에 None이 아닌 값이 남아 있습니다.")
        # else:
        #     print("Single_Order 반복문 이상무!!")
        
        ###############################################################
        # 같은 매커니즘으로 Original_Single_Order도 bundle이랑 합쳐주기
        for i in range(len(Original_Single_Order)):
            best_merge = None
            best_cost_reduction = float('-inf')
            current_order = Original_Single_Order[i]

            # 무작위 탐색 20%의 확률
            if random.random() < 1-k3:
                # 무작위로 번들을 선택하여 합치기
                if i+1 < len(Single_Order):
                    potential_bundles = Multi_Order + Original_Single_Order[i+1:]
                else:
                    potential_bundles = Multi_Order
                random.shuffle(potential_bundles)  # 번들을 무작위로 섞기
                for potential_bundle in potential_bundles:
                    merged_bundle = combine(all_orders, all_riders, dist_mat, potential_bundle, current_order)
                    if merged_bundle:
                        best_merge = (current_order, potential_bundle, merged_bundle)
                        break  # 무작위로 첫 feasible한 번들을 찾으면 합치기

            else:
                # 탐욕적 방법으로 번들 결합
                for MO in Multi_Order:
                    merged_bundle = combine(all_orders, all_riders, dist_mat, MO, current_order)
                    if merged_bundle:
                        cost_reduction = MO.cost + current_order.cost - merged_bundle.cost
                        if cost_reduction > best_cost_reduction:
                            best_cost_reduction = cost_reduction
                            best_merge = (current_order, MO, merged_bundle)

                if i+1 < len(Single_Order):
                    for OSO in Original_Single_Order[i+1:]:
                        merged_bundle = combine(all_orders, all_riders, dist_mat, OSO, current_order)
                        if merged_bundle:
                            cost_reduction = OSO.cost + current_order.cost - merged_bundle.cost
                            if cost_reduction > best_cost_reduction:
                                best_cost_reduction = cost_reduction
                                best_merge = (current_order, OSO, merged_bundle)

            if best_merge:
                best_merger = best_merge[1]
                merge_bundle = best_merge[2]

                current_order.rider.available_number += 1
                best_merger.rider.available_number += 1

                merge_bundle.rider.available_number -=1

                if best_merger in Multi_Order:
                    Multi_Order.remove(best_merger)
                elif best_merger in Original_Single_Order:
                    Original_Single_Order.remove(best_merger)

                Multi_Order.append(merge_bundle)

            else:
                print(f'{Original_Single_Order[i].shop_seq}는 다른 bundle과 전부 infeasible')
                Multi_Order.append(current_order)


            Original_Single_Order[i] = None #None으로 설정하여 반복문에서 len 안달라지게끔
                
            if i == len(Original_Single_Order)-1 :
                break

        # Original_Single_Order 리스트 체크
        non_none_orders = [order for order in Original_Single_Order if order is not None]

        # None이 아닌 값들이 남아있다면 에러 메시지와 함께 그 값들을 출력
        if non_none_orders:
            print("error: Original_Single_Order 리스트에 None이 아닌 값이 남아 있습니다.")
            print("None이 아닌 값들:", non_none_orders)
        # else:
        #      print("Original_Single_Order 이상무")

        return Multi_Order

    

    ##################################(MAIN CODE)##################################

    best_avg_cost = float('inf')
    best_solution = None

    while time.time() - start_time < (timelimit-7) :
        all_bundles = greedy_dv_mg(all_bundles)
        current_avg_cost = get_avg_cost(all_orders, all_bundles)
        print(f'Current avg_cost : {current_avg_cost}')
        
        if current_avg_cost < best_avg_cost:
            best_avg_cost = current_avg_cost
            best_solution = [
                [bundle.rider.type, bundle.shop_seq, bundle.dlv_seq]
                for bundle in all_bundles
            ]
        if time.time() - start_time > (timelimit-5) :
            return best_solution

    solution = best_solution

    #------------- End of custom algorithm code--------------#

    return solution
